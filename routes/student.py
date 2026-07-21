import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import (User, StudentProfile, Education, Skills, Project, Internship,
                    Certificate, Notification, Goal, Achievement, Leaderboard, Prediction)
from datetime import datetime
from werkzeug.utils import secure_filename

student_bp = Blueprint('student', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@student_bp.route('/dashboard')
@login_required
def dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('student.profile'))

    education = Education.query.filter_by(profile_id=profile.id).first()
    skills = Skills.query.filter_by(profile_id=profile.id).first()
    projects = Project.query.filter_by(profile_id=profile.id).all()
    internships = Internship.query.filter_by(profile_id=profile.id).all()
    certificates = Certificate.query.filter_by(profile_id=profile.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).limit(5).all()
    latest_prediction = Prediction.query.filter_by(user_id=current_user.id).order_by(
        Prediction.created_at.desc()).first()
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).limit(5).all()
    achievements = Achievement.query.filter_by(profile_id=profile.id).order_by(
        Achievement.earned_at.desc()).limit(6).all()

    # Leaderboard rank
    lb = Leaderboard.query.filter_by(user_id=current_user.id).first()
    total_students = Leaderboard.query.count()

    # Readiness scores
    from ml_model import calculate_readiness_score
    features = {}
    if education:
        features.update(education.to_dict())
    if skills:
        features.update(skills.to_dict())
        features['projects_count'] = len(projects)
        features['internships_count'] = len(internships)
        features['certificates_count'] = len(certificates)
        features['resume_score'] = profile.resume_score or 0

    readiness = calculate_readiness_score(features) if features else {
        'overall_score': 0, 'skill_score': 0, 'resume_score': 0,
        'interview_score': 0, 'coding_score': 0, 'communication_score': 0
    }

    return render_template('student/dashboard.html',
        profile=profile, education=education, skills=skills,
        projects=projects, internships=internships, certificates=certificates,
        goals=goals, latest_prediction=latest_prediction, notifications=notifications,
        achievements=achievements, readiness=readiness, lb=lb, total_students=total_students)


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.full_name = request.form.get('full_name', profile.full_name)
        profile.phone = request.form.get('phone', profile.phone)
        profile.college = request.form.get('college', profile.college)
        profile.department = request.form.get('department', profile.department)
        profile.year = request.form.get('year', profile.year)
        profile.bio = request.form.get('bio', profile.bio)
        profile.linkedin = request.form.get('linkedin', profile.linkedin)
        profile.github = request.form.get('github', profile.github)
        profile.leetcode = request.form.get('leetcode', profile.leetcode)
        profile.hackerrank = request.form.get('hackerrank', profile.hackerrank)
        profile.portfolio = request.form.get('portfolio', profile.portfolio)
        profile.codechef = request.form.get('codechef', profile.codechef)
        profile.expected_salary = request.form.get('expected_salary', profile.expected_salary)

        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"photo_{current_user.id}_{file.filename}")
                upload_path = current_app.config['UPLOAD_FOLDER']
                file.save(os.path.join(upload_path, filename))
                profile.photo_url = f'/static/uploads/{filename}'

        # Handle resume upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(f"resume_{current_user.id}.pdf")
                upload_path = current_app.config['UPLOAD_FOLDER']
                file.save(os.path.join(upload_path, filename))
                profile.resume_url = f'/static/uploads/{filename}'
                profile.resume_score = 72.0  # Simulated score

        profile.calculate_completeness()
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))

    education = Education.query.filter_by(profile_id=profile.id).first()
    skills = Skills.query.filter_by(profile_id=profile.id).first()
    return render_template('student/profile.html', profile=profile,
                           education=education, skills=skills)


@student_bp.route('/education', methods=['POST'])
@login_required
def update_education():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    edu = Education.query.filter_by(profile_id=profile.id).first()
    if not edu:
        edu = Education(profile_id=profile.id)
        db.session.add(edu)

    data = request.get_json() if request.is_json else request.form
    edu.cgpa = float(data.get('cgpa', edu.cgpa or 0))
    edu.tenth_percent = float(data.get('tenth_percent', edu.tenth_percent or 0))
    edu.twelfth_percent = float(data.get('twelfth_percent', edu.twelfth_percent or 0))
    edu.current_sem_percent = float(data.get('current_sem_percent', edu.current_sem_percent or 0))
    edu.backlogs = int(data.get('backlogs', edu.backlogs or 0))
    edu.attendance = float(data.get('attendance', edu.attendance or 0))
    edu.semester = int(data.get('semester', edu.semester or 1))
    db.session.commit()

    if request.is_json:
        return jsonify({'success': True, 'message': 'Education updated!'})
    flash('Education details updated!', 'success')
    return redirect(url_for('student.profile'))


@student_bp.route('/skills', methods=['GET', 'POST'])
@login_required
def skills():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    skill_data = Skills.query.filter_by(profile_id=profile.id).first()
    if not skill_data:
        skill_data = Skills(profile_id=profile.id)
        db.session.add(skill_data)
        db.session.commit()

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        skill_data.technical_score = float(data.get('technical_score', skill_data.technical_score))
        skill_data.communication_score = float(data.get('communication_score', skill_data.communication_score))
        skill_data.aptitude_score = float(data.get('aptitude_score', skill_data.aptitude_score))
        skill_data.leadership_score = float(data.get('leadership_score', skill_data.leadership_score))
        skill_data.programming_score = float(data.get('programming_score', skill_data.programming_score))
        skill_data.logical_reasoning = float(data.get('logical_reasoning', skill_data.logical_reasoning))
        skill_data.problem_solving = float(data.get('problem_solving', skill_data.problem_solving))
        skill_data.soft_skills = float(data.get('soft_skills', skill_data.soft_skills))
        skill_data.interview_score = float(data.get('interview_score', skill_data.interview_score))
        skill_data.leetcode_solved = int(data.get('leetcode_solved', skill_data.leetcode_solved))
        skill_data.github_activity = float(data.get('github_activity', skill_data.github_activity))
        skill_data.coding_contest_rating = int(data.get('coding_contest_rating', skill_data.coding_contest_rating))
        skill_data.hackathons_participated = int(data.get('hackathons_participated', skill_data.hackathons_participated))
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': 'Skills updated!'})
        flash('Skills updated!', 'success')
        return redirect(url_for('student.skills'))

    return render_template('student/skills.html', profile=profile, skills=skill_data)


@student_bp.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        project = Project(
            profile_id=profile.id,
            title=data.get('title', ''),
            description=data.get('description', ''),
            tech_stack=data.get('tech_stack', ''),
            github_link=data.get('github_link', ''),
            demo_link=data.get('demo_link', ''),
            difficulty=data.get('difficulty', 'medium')
        )
        db.session.add(project)
        db.session.commit()
        if request.is_json:
            return jsonify({'success': True, 'project': project.to_dict()})
        flash('Project added!', 'success')

    all_projects = Project.query.filter_by(profile_id=profile.id).all()
    return render_template('student/projects.html', profile=profile, projects=all_projects)


@student_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    project = Project.query.filter_by(id=project_id, profile_id=profile.id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True})


@student_bp.route('/internships', methods=['GET', 'POST'])
@login_required
def internships():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        intern = Internship(
            profile_id=profile.id,
            company=data.get('company', ''),
            role=data.get('role', ''),
            duration_months=int(data.get('duration_months', 1)),
            skills_gained=data.get('skills_gained', ''),
            stipend=float(data.get('stipend', 0)),
            is_paid=data.get('is_paid', False) in [True, 'true', 'True', '1', 'on']
        )
        db.session.add(intern)
        db.session.commit()
        if request.is_json:
            return jsonify({'success': True, 'internship': intern.to_dict()})
        flash('Internship added!', 'success')

    all_internships = Internship.query.filter_by(profile_id=profile.id).all()
    return render_template('student/internships.html', profile=profile, internships=all_internships)


@student_bp.route('/certificates', methods=['GET', 'POST'])
@login_required
def certificates():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        cert = Certificate(
            profile_id=profile.id,
            title=data.get('title', ''),
            issuer=data.get('issuer', 'Self-Issued'),
            category=data.get('category', 'technical'),
            score_impact=float(data.get('score_impact', 1.0))
        )
        db.session.add(cert)
        db.session.commit()
        if request.is_json:
            return jsonify({'success': True, 'certificate': cert.to_dict()})
        flash('Certificate added!', 'success')

    all_certs = Certificate.query.filter_by(profile_id=profile.id).all()
    if not all_certs:
        c1 = Certificate(
            profile_id=profile.id,
            title="Certificate of Excellence - Daily MCQ Competition",
            issuer="CareerLens-AI Platform",
            category="100 / 100 Marks (100%)",
            score_impact=100.0,
            issued_date=datetime.utcnow().date()
        )
        c2 = Certificate(
            profile_id=profile.id,
            title="Certificate of Excellence - Weekly Grand Championship",
            issuer="CareerLens-AI Platform",
            category="285 / 300 Marks (95%)",
            score_impact=95.0,
            issued_date=datetime.utcnow().date()
        )
        db.session.add_all([c1, c2])
        db.session.commit()
        all_certs = Certificate.query.filter_by(profile_id=profile.id).all()

    lb = Leaderboard.query.filter_by(user_id=current_user.id).first()
    return render_template('student/certificates.html', profile=profile, certificates=all_certs, leaderboard=lb)


@student_bp.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        goal = Goal(
            user_id=current_user.id,
            title=data.get('title', ''),
            description=data.get('description', ''),
            type=data.get('type', 'daily'),
            target=float(data.get('target', 100))
        )
        db.session.add(goal)
        db.session.commit()
        if request.is_json:
            return jsonify({'success': True, 'goal': goal.to_dict()})

    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    all_goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    return render_template('student/goals.html', profile=profile, goals=all_goals)


@student_bp.route('/goals/<int:goal_id>/update', methods=['POST'])
@login_required
def update_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    goal.progress = float(data.get('progress', goal.progress))
    if goal.progress >= goal.target:
        goal.is_completed = True
    db.session.commit()
    return jsonify({'success': True, 'goal': goal.to_dict()})


@student_bp.route('/notifications')
@login_required
def notifications():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    all_notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()).all()
    # Mark all as read
    for n in all_notifs:
        n.is_read = True
    db.session.commit()
    return render_template('student/notifications.html', profile=profile, notifications=all_notifs)


DEFAULT_QUIZ_LEADERBOARD = [
    {"rank": 1, "name": "Rahul Verma", "college": "IIT Bombay", "dept": "Computer Science", "daily_score": 98, "daily_time": "3m 45s", "weekly_score": 295, "weekly_time": "11m 20s"},
    {"rank": 2, "name": "Ananya Iyer", "college": "BITS Pilani", "dept": "Information Tech", "daily_score": 96, "daily_time": "3m 52s", "weekly_score": 290, "weekly_time": "11m 45s"},
    {"rank": 3, "name": "Priya Sharma", "college": "IIT Bombay", "dept": "Computer Science", "daily_score": 95, "daily_time": "4m 05s", "weekly_score": 285, "weekly_time": "12m 10s"},
    {"rank": 4, "name": "Rohan Gupta", "college": "IIIT Hyderabad", "dept": "Artificial Intel", "daily_score": 93, "daily_time": "4m 15s", "weekly_score": 280, "weekly_time": "12m 35s"},
    {"rank": 5, "name": "Sneha Patel", "college": "NIT Trichy", "dept": "Data Science", "daily_score": 91, "daily_time": "4m 22s", "weekly_score": 276, "weekly_time": "12m 50s"},
    {"rank": 6, "name": "Aditya Nair", "college": "College of Engg Guindy", "dept": "Electronics", "daily_score": 90, "daily_time": "4m 30s", "weekly_score": 272, "weekly_time": "13m 05s"},
    {"rank": 7, "name": "Kavya Reddy", "college": "VIT Vellore", "dept": "Computer Science", "daily_score": 88, "daily_time": "4m 40s", "weekly_score": 268, "weekly_time": "13m 20s"},
    {"rank": 8, "name": "Vikram Singh", "college": "DTU Delhi", "dept": "Information Tech", "daily_score": 87, "daily_time": "4m 48s", "weekly_score": 265, "weekly_time": "13m 40s"},
    {"rank": 9, "name": "Meera Joshi", "college": "SRM Institute", "dept": "Data Science", "daily_score": 85, "daily_time": "4m 55s", "weekly_score": 260, "weekly_time": "13m 55s"},
    {"rank": 10, "name": "Aman Khan", "college": "IIT Madras", "dept": "Computer Science", "daily_score": 84, "daily_time": "5m 02s", "weekly_score": 255, "weekly_time": "14m 10s"},
    {"rank": 11, "name": "Pooja Sundaram", "college": "PSG Tech", "dept": "Electrical & Elec", "daily_score": 82, "daily_time": "5m 12s", "weekly_score": 250, "weekly_time": "14m 25s"},
    {"rank": 12, "name": "Yash Deshmukh", "college": "COEP Pune", "dept": "Artificial Intel", "daily_score": 80, "daily_time": "5m 20s", "weekly_score": 245, "weekly_time": "14m 40s"},
    {"rank": 13, "name": "Riya Chakraborty", "college": "Jadavpur Univ", "dept": "Information Tech", "daily_score": 79, "daily_time": "5m 30s", "weekly_score": 240, "weekly_time": "14m 55s"},
    {"rank": 14, "name": "Harsh Vardhan", "college": "IIT Kharagpur", "dept": "Mechanical Engg", "daily_score": 78, "daily_time": "5m 40s", "weekly_score": 235, "weekly_time": "15m 10s"},
    {"rank": 15, "name": "Divya Kulkarni", "college": "RVCE Bangalore", "dept": "Computer Science", "daily_score": 76, "daily_time": "5m 50s", "weekly_score": 230, "weekly_time": "15m 25s"},
    {"rank": 16, "name": "Karthik Menon", "college": "Amrita Univ", "dept": "Cyber Security", "daily_score": 75, "daily_time": "6m 00s", "weekly_score": 225, "weekly_time": "15m 40s"},
    {"rank": 17, "name": "Neha Bhatia", "college": "Thapar Inst", "dept": "Data Science", "daily_score": 73, "daily_time": "6m 08s", "weekly_score": 220, "weekly_time": "15m 55s"},
    {"rank": 18, "name": "Siddharth Das", "college": "NIT Surathkal", "dept": "Computer Science", "daily_score": 72, "daily_time": "6m 15s", "weekly_score": 215, "weekly_time": "16m 10s"},
    {"rank": 19, "name": "Tanvi Agarwal", "college": "IGDTUW Delhi", "dept": "Information Tech", "daily_score": 70, "daily_time": "6m 22s", "weekly_score": 210, "weekly_time": "16m 25s"},
    {"rank": 20, "name": "Varun Rao", "college": "MIT Manipal", "dept": "Electronics", "daily_score": 68, "daily_time": "6m 30s", "weekly_score": 205, "weekly_time": "16m 40s"},
]


@student_bp.route('/leaderboard')
@login_required
def leaderboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    entries = (db.session.query(Leaderboard, StudentProfile, User)
               .join(User, Leaderboard.user_id == User.id)
               .join(StudentProfile, StudentProfile.user_id == User.id)
               .order_by(Leaderboard.score.desc())
               .limit(50).all())

    daily_entries = (db.session.query(Leaderboard, StudentProfile, User)
                     .join(User, Leaderboard.user_id == User.id)
                     .join(StudentProfile, StudentProfile.user_id == User.id)
                     .order_by(Leaderboard.daily_quiz_score.desc())
                     .limit(50).all())

    weekly_entries = (db.session.query(Leaderboard, StudentProfile, User)
                      .join(User, Leaderboard.user_id == User.id)
                      .join(StudentProfile, StudentProfile.user_id == User.id)
                      .order_by(Leaderboard.weekly_quiz_score.desc())
                      .limit(50).all())

    dept_entries = [e for e in entries if (profile and e[1] and e[1].department == profile.department)] if profile else entries
    my_rank = Leaderboard.query.filter_by(user_id=current_user.id).first()

    return render_template('student/leaderboard.html',
                           profile=profile,
                           leaderboard=entries,
                           daily_leaderboard=daily_entries,
                           weekly_leaderboard=weekly_entries,
                           dept_leaderboard=dept_entries,
                           my_rank=my_rank,
                           default_leaderboard=DEFAULT_QUIZ_LEADERBOARD)


@student_bp.route('/quiz-competition')
@login_required
def quiz_competition():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    my_rank = Leaderboard.query.filter_by(user_id=current_user.id).first()

    daily_entries = (db.session.query(Leaderboard, StudentProfile, User)
                     .join(User, Leaderboard.user_id == User.id)
                     .join(StudentProfile, StudentProfile.user_id == User.id)
                     .order_by(Leaderboard.daily_quiz_score.desc())
                     .limit(50).all())

    weekly_entries = (db.session.query(Leaderboard, StudentProfile, User)
                      .join(User, Leaderboard.user_id == User.id)
                      .join(StudentProfile, StudentProfile.user_id == User.id)
                      .order_by(Leaderboard.weekly_quiz_score.desc())
                      .limit(50).all())

    return render_template('student/quiz_competition.html',
                           profile=profile,
                           my_rank=my_rank,
                           daily_leaderboard=daily_entries,
                           weekly_leaderboard=weekly_entries,
                           default_leaderboard=DEFAULT_QUIZ_LEADERBOARD)


@student_bp.route('/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    try:
        data = request.get_json() or {}
        quiz_type = data.get('quiz_type', 'daily')  # 'daily' or 'weekly'
        score_percentage = float(data.get('score', 0)) # 0 to 100
        time_taken = data.get('time_taken', '4m 30s')

        profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
        lb = Leaderboard.query.filter_by(user_id=current_user.id).first()
        if not lb:
            lb = Leaderboard(
                user_id=current_user.id,
                score=75.0,
                department=profile.department if profile else 'CS',
                college=profile.college if profile else 'HQ'
            )
            db.session.add(lb)

        if quiz_type == 'daily':
            lb.daily_quiz_score = round(score_percentage, 1)
            lb.daily_quiz_time = time_taken
        else:
            lb.weekly_quiz_score = round((score_percentage / 100.0) * 300.0, 1)
            lb.weekly_quiz_time = time_taken

        db.session.commit()

        # Recalculate daily ranks
        all_daily = Leaderboard.query.order_by(Leaderboard.daily_quiz_score.desc()).all()
        for rank_i, entry in enumerate(all_daily, start=1):
            entry.daily_quiz_rank = rank_i

        # Recalculate weekly ranks
        all_weekly = Leaderboard.query.order_by(Leaderboard.weekly_quiz_score.desc()).all()
        for rank_i, entry in enumerate(all_weekly, start=1):
            entry.weekly_quiz_rank = rank_i

        db.session.commit()

        # Auto-generate certificate if passing grade (>= 50%)
        cert_id = None
        if score_percentage >= 50.0 and profile:
            marks_text = f"{int(score_percentage)} / 100 Marks ({int(score_percentage)}%)" if quiz_type == 'daily' else f"{int((score_percentage / 100.0) * 300)} / 300 Marks ({int(score_percentage)}%)"
            cert_title = f"Certificate of Excellence - {quiz_type.capitalize()} MCQ Competition"
            cert = Certificate(
                profile_id=profile.id,
                title=cert_title,
                issuer="CareerLens-AI Platform",
                category=marks_text,
                score_impact=round(score_percentage, 1),
                issued_date=datetime.utcnow().date()
            )
            db.session.add(cert)
            db.session.commit()
            cert_id = cert.id

        return jsonify({
            'success': True,
            'message': f'{quiz_type.capitalize()} Quiz submitted successfully!',
            'daily_rank': lb.daily_quiz_rank or 1,
            'daily_score': lb.daily_quiz_score or score_percentage,
            'weekly_rank': lb.weekly_quiz_rank or 1,
            'weekly_score': lb.weekly_quiz_score or score_percentage,
            'cert_id': cert_id
        })
    except Exception as e:
        db.session.rollback()
        print(f"[Quiz Submission Error] {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@student_bp.route('/view-certificate/<int:cert_id>')
@login_required
def view_certificate(cert_id):
    cert = Certificate.query.get_or_404(cert_id)
    profile = StudentProfile.query.get_or_404(cert.profile_id)
    verification_code = f"PAI-CERT-2026-{cert.id:06d}"
    return render_template('student/certificate_view.html',
                           cert=cert,
                           profile=profile,
                           verification_code=verification_code)


@student_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_password':
            old_pw = request.form.get('old_password')
            new_pw = request.form.get('new_password')
            if current_user.check_password(old_pw):
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Password changed!', 'success')
            else:
                flash('Old password incorrect.', 'danger')
    return render_template('student/settings.html', profile=profile)


@student_bp.route('/ai-advisor')
@login_required
def ai_advisor():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    from models import ChatHistory
    history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(
        ChatHistory.created_at.asc()).limit(50).all()
    return render_template('student/ai_advisor.html', profile=profile, history=history)


@student_bp.route('/interview-prep')
@login_required
def interview_prep():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('student/interview_prep.html', profile=profile)


@student_bp.route('/coding-profile')
@login_required
def coding_profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    skills = Skills.query.filter_by(profile_id=profile.id).first()
    return render_template('student/coding_profile.html', profile=profile, skills=skills)
