from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import User, StudentProfile, Education, Skills, Prediction, Company, Leaderboard, ActivityLog, Notification
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_students = User.query.filter_by(role='student').count()
    total_predictions = Prediction.query.count()
    placed_count = Prediction.query.filter_by(result='Placed').count()
    placement_rate = (placed_count / total_predictions * 100) if total_predictions > 0 else 0

    recent_students = (db.session.query(User, StudentProfile)
                       .join(StudentProfile, StudentProfile.user_id == User.id)
                       .filter(User.role == 'student')
                       .order_by(User.created_at.desc())
                       .limit(10).all())

    recent_predictions = (Prediction.query
                          .order_by(Prediction.created_at.desc())
                          .limit(10).all())

    # Department-wise stats
    dept_stats = (db.session.query(StudentProfile.department, db.func.count(StudentProfile.id))
                  .group_by(StudentProfile.department)
                  .filter(StudentProfile.department.isnot(None))
                  .all())

    # Weekly registrations
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_new = User.query.filter(User.created_at >= week_ago, User.role == 'student').count()

    top_students = (db.session.query(Leaderboard, StudentProfile, User)
                   .join(User, Leaderboard.user_id == User.id)
                   .join(StudentProfile, StudentProfile.user_id == User.id)
                   .order_by(Leaderboard.score.desc())
                   .limit(5).all())

    return render_template('admin/dashboard.html',
        total_students=total_students,
        total_predictions=total_predictions,
        placement_rate=round(placement_rate, 1),
        placed_count=placed_count,
        recent_students=recent_students,
        recent_predictions=recent_predictions,
        dept_stats=dept_stats,
        weekly_new=weekly_new,
        top_students=top_students)


@admin_bp.route('/students')
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '')
    dept = request.args.get('dept', '')

    query = (db.session.query(User, StudentProfile)
             .join(StudentProfile, StudentProfile.user_id == User.id, isouter=True)
             .filter(User.role == 'student'))

    if search:
        query = query.filter(
            db.or_(User.email.ilike(f'%{search}%'),
                   StudentProfile.full_name.ilike(f'%{search}%'),
                   StudentProfile.college.ilike(f'%{search}%')))
    if dept:
        query = query.filter(StudentProfile.department == dept)

    students_page = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)

    departments = db.session.query(StudentProfile.department).distinct().filter(
        StudentProfile.department.isnot(None)).all()
    departments = [d[0] for d in departments]

    return render_template('admin/students.html',
        students=students_page, departments=departments,
        search=search, dept=dept)


@admin_bp.route('/students/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_student(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({'success': False, 'message': 'Cannot delete admin.'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/students/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_student_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active})


@admin_bp.route('/companies', methods=['GET', 'POST'])
@admin_required
def companies():
    import json
    if request.method == 'POST':
        data = request.form
        company = Company(
            name=data.get('name'),
            min_cgpa=float(data.get('min_cgpa', 6.0)),
            package_lpa=float(data.get('package_lpa', 0)),
            max_backlogs=int(data.get('max_backlogs', 0)),
            required_skills=json.dumps(data.get('required_skills', '').split(',')),
            description=data.get('description', '')
        )
        db.session.add(company)
        db.session.commit()
        flash('Company added!', 'success')

    all_companies = Company.query.order_by(Company.package_lpa.desc()).all()
    return render_template('admin/companies.html', companies=all_companies)


@admin_bp.route('/companies/<int:company_id>/delete', methods=['POST'])
@admin_required
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    db.session.delete(company)
    db.session.commit()
    return jsonify({'success': True})


@admin_bp.route('/reports')
@admin_required
def reports():
    predictions = (db.session.query(Prediction, User, StudentProfile)
                   .join(User, Prediction.user_id == User.id)
                   .join(StudentProfile, StudentProfile.user_id == User.id, isouter=True)
                   .order_by(Prediction.created_at.desc())
                   .limit(100).all())

    dept_placement = (db.session.query(
        StudentProfile.department,
        db.func.count(Prediction.id),
        db.func.sum(db.case((Prediction.result == 'Placed', 1), else_=0))
    ).join(User, StudentProfile.user_id == User.id)
     .join(Prediction, Prediction.user_id == User.id, isouter=True)
     .group_by(StudentProfile.department)
     .filter(StudentProfile.department.isnot(None))
     .all())

    return render_template('admin/reports.html',
        predictions=predictions, dept_placement=dept_placement)


@admin_bp.route('/notify-all', methods=['POST'])
@admin_required
def notify_all():
    data = request.get_json() or request.form
    students = User.query.filter_by(role='student').all()
    for student in students:
        notif = Notification(
            user_id=student.id,
            title=data.get('title', 'Admin Announcement'),
            message=data.get('message', ''),
            type=data.get('type', 'info')
        )
        db.session.add(notif)
    db.session.commit()
    return jsonify({'success': True, 'sent_to': len(students)})


@admin_bp.route('/activity-logs')
@admin_required
def activity_logs():
    logs = (db.session.query(ActivityLog, User)
            .join(User, ActivityLog.user_id == User.id)
            .order_by(ActivityLog.created_at.desc())
            .limit(200).all())
    return render_template('admin/activity_logs.html', logs=logs)
