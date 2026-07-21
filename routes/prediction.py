import json
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import StudentProfile, Education, Skills, Project, Internship, Certificate, Prediction, Notification, Company, Leaderboard
from ml_model import predict_placement, calculate_readiness_score
from datetime import datetime

prediction_bp = Blueprint('predict', __name__)


@prediction_bp.route('/', methods=['GET', 'POST'])
@login_required
def predict():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    education = Education.query.filter_by(profile_id=profile.id).first() if profile else None
    skills = Skills.query.filter_by(profile_id=profile.id).first() if profile else None
    projects = Project.query.filter_by(profile_id=profile.id).all() if profile else []
    internships = Internship.query.filter_by(profile_id=profile.id).all() if profile else []
    certificates = Certificate.query.filter_by(profile_id=profile.id).all() if profile else []

    prediction_history = Prediction.query.filter_by(
        user_id=current_user.id).order_by(Prediction.created_at.desc()).limit(10).all()

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Build features
        features = {}
        if education:
            features.update({
                'cgpa': education.cgpa or 0,
                'tenth_percent': education.tenth_percent or 0,
                'twelfth_percent': education.twelfth_percent or 0,
                'current_sem_percent': education.current_sem_percent or 0,
                'backlogs': education.backlogs or 0,
                'attendance': education.attendance or 0,
            })
        if skills:
            features.update({
                'technical_score': skills.technical_score or 0,
                'communication_score': skills.communication_score or 0,
                'aptitude_score': skills.aptitude_score or 0,
                'leadership_score': skills.leadership_score or 0,
                'programming_score': skills.programming_score or 0,
                'logical_reasoning': skills.logical_reasoning or 0,
                'problem_solving': skills.problem_solving or 0,
                'soft_skills': skills.soft_skills or 0,
                'interview_score': skills.interview_score or 0,
                'leetcode_solved': skills.leetcode_solved or 0,
                'github_activity': skills.github_activity or 0,
                'coding_contest_rating': skills.coding_contest_rating or 0,
                'hackathons_count': skills.hackathons_participated or 0,
            })

        features.update({
            'projects_count': len(projects),
            'internships_count': len(internships),
            'certificates_count': len(certificates),
            'resume_score': profile.resume_score or 0,
        })

        # Override with form data if provided
        for key in features:
            if data.get(key):
                try:
                    features[key] = float(data.get(key))
                except (ValueError, TypeError):
                    pass

        # Run prediction
        result = predict_placement(features)
        readiness = calculate_readiness_score(features)

        # Save prediction
        pred = Prediction(
            user_id=current_user.id,
            probability=result['probability'],
            result=result['result'],
            confidence=result['confidence'],
            placement_score=result['placement_score'],
            strengths=json.dumps(result['strengths']),
            weaknesses=json.dumps(result['weaknesses']),
            suggestions=json.dumps(result['suggestions']),
            input_snapshot=json.dumps(features)
        )
        db.session.add(pred)

        # Update leaderboard
        lb = Leaderboard.query.filter_by(user_id=current_user.id).first()
        if not lb:
            lb = Leaderboard(user_id=current_user.id)
            db.session.add(lb)
        lb.score = result['placement_score']
        lb.department = profile.department if profile else ''
        lb.college = profile.college if profile else ''

        # Notification
        notif = Notification(
            user_id=current_user.id,
            title=f'Prediction Complete: {result["result"]}',
            message=f'Your placement probability is {result["probability"]:.1f}%. Check your dashboard for details.',
            type='success' if result['result'] == 'Placed' else 'warning'
        )
        db.session.add(notif)
        db.session.commit()

        # Re-rank leaderboard
        _update_ranks()

        if request.is_json:
            return jsonify({
                'success': True,
                'prediction': result,
                'readiness': readiness,
                'prediction_id': pred.id
            })

        flash(f'Prediction complete! Result: {result["result"]} ({result["probability"]:.1f}%)', 'success')
        return redirect(url_for('predict.result', prediction_id=pred.id))

    # Company eligibility
    companies = Company.query.filter(Company.is_active == True).all()
    eligible_companies = []
    if education and skills:
        for company in companies:
            if (education.cgpa or 0) >= company.min_cgpa and (education.backlogs or 0) <= company.max_backlogs:
                eligible_companies.append(company)

    return render_template('student/prediction.html',
        profile=profile, education=education, skills=skills,
        projects=projects, internships=internships, certificates=certificates,
        prediction_history=prediction_history, companies=companies,
        eligible_companies=eligible_companies)


@prediction_bp.route('/result/<int:prediction_id>')
@login_required
def result(prediction_id):
    pred = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first_or_404()
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('student/prediction_result.html', prediction=pred, profile=profile)


@prediction_bp.route('/history')
@login_required
def history():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    all_predictions = Prediction.query.filter_by(
        user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    return render_template('student/prediction_history.html',
                           profile=profile, predictions=all_predictions)


@prediction_bp.route('/eligible-companies')
@login_required
def eligible_companies():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    education = Education.query.filter_by(profile_id=profile.id).first() if profile else None
    skills = Skills.query.filter_by(profile_id=profile.id).first() if profile else None

    companies = Company.query.filter(Company.is_active == True).all()
    eligible = []
    not_eligible = []

    if education:
        cgpa = education.cgpa or 0
        backlogs = education.backlogs or 0
        for c in companies:
            if cgpa >= c.min_cgpa and backlogs <= c.max_backlogs:
                eligible.append(c)
            else:
                not_eligible.append(c)
    else:
        not_eligible = companies

    return render_template('student/eligible_companies.html',
        profile=profile, eligible=eligible, not_eligible=not_eligible)


def _update_ranks():
    """Recalculate and update leaderboard ranks."""
    entries = Leaderboard.query.order_by(Leaderboard.score.desc()).all()
    for i, entry in enumerate(entries):
        entry.rank = i + 1
    db.session.commit()
