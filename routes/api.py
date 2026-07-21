from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import (StudentProfile, Education, Skills, Project, Internship, Certificate,
                    Prediction, Notification, Goal, Leaderboard, User)
from datetime import datetime

api_bp = Blueprint('api', __name__)


@api_bp.route('/student/profile')
@login_required
def get_profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'success': False, 'message': 'Profile not found'}), 404
    return jsonify({'success': True, 'profile': profile.to_dict()})


@api_bp.route('/student/dashboard-data')
@login_required
def dashboard_data():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return jsonify({'success': False}), 404

    education = Education.query.filter_by(profile_id=profile.id).first()
    skills = Skills.query.filter_by(profile_id=profile.id).first()
    projects = Project.query.filter_by(profile_id=profile.id).count()
    internships = Internship.query.filter_by(profile_id=profile.id).count()
    certificates = Certificate.query.filter_by(profile_id=profile.id).count()
    latest_pred = Prediction.query.filter_by(user_id=current_user.id).order_by(
        Prediction.created_at.desc()).first()

    return jsonify({
        'success': True,
        'profile': profile.to_dict(),
        'education': education.to_dict() if education else {},
        'skills': skills.to_dict() if skills else {},
        'counts': {'projects': projects, 'internships': internships, 'certificates': certificates},
        'latest_prediction': latest_pred.to_dict() if latest_pred else None,
    })


@api_bp.route('/notifications')
@login_required
def get_notifications():
    notifs = Notification.query.filter_by(
        user_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({
        'success': True,
        'notifications': [n.to_dict() for n in notifs],
        'unread_count': unread
    })


@api_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/leaderboard')
@login_required
def leaderboard():
    entries = (db.session.query(Leaderboard, StudentProfile, User)
               .join(User, Leaderboard.user_id == User.id)
               .join(StudentProfile, StudentProfile.user_id == User.id)
               .order_by(Leaderboard.score.desc())
               .limit(50).all())

    result = []
    for i, (lb, profile, user) in enumerate(entries):
        result.append({
            'rank': i + 1,
            'name': profile.full_name or user.email.split('@')[0],
            'college': profile.college,
            'department': profile.department,
            'score': lb.score,
            'is_me': user.id == current_user.id,
            'photo': profile.photo_url,
        })

    return jsonify({'success': True, 'leaderboard': result})


@api_bp.route('/analytics/prediction-trend')
@login_required
def prediction_trend():
    predictions = Prediction.query.filter_by(
        user_id=current_user.id).order_by(Prediction.created_at.asc()).all()

    data = [{
        'date': p.created_at.strftime('%Y-%m-%d'),
        'probability': p.probability,
        'score': p.placement_score,
    } for p in predictions]

    return jsonify({'success': True, 'data': data})


@api_bp.route('/goals/<int:goal_id>/update', methods=['POST'])
@login_required
def update_goal(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    goal.progress = float(data.get('progress', goal.progress))
    if goal.progress >= goal.target:
        goal.is_completed = True
    db.session.commit()
    return jsonify({'success': True, 'goal': goal.to_dict()})


@api_bp.route('/stats/overview')
@login_required
def stats_overview():
    """Admin-level overview stats."""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    total_students = User.query.filter_by(role='student').count()
    total_predictions = Prediction.query.count()
    placed = Prediction.query.filter_by(result='Placed').count()

    return jsonify({
        'success': True,
        'total_students': total_students,
        'total_predictions': total_predictions,
        'placement_rate': round((placed / total_predictions * 100) if total_predictions else 0, 1),
    })
