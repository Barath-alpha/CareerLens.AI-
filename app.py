import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from flask_cors import CORS
from config import config
from extensions import db, login_manager, mail
from models import User, StudentProfile, Education, Skills, Project, Internship, Certificate
from models import Prediction, Notification, Goal, Achievement, Company, Leaderboard, ChatHistory, ActivityLog
from datetime import datetime

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    CORS(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.prediction import prediction_bp
    from routes.admin import admin_bp
    from routes.ai_routes import ai_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(prediction_bp, url_prefix='/predict')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(ai_bp, url_prefix='/ai')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Main routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    @app.route('/submit-quiz', methods=['POST'])
    @login_required
    def submit_quiz_fallback():
        from routes.student import submit_quiz
        return submit_quiz()

    # Error handlers
    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Context processors
    @app.context_processor
    def inject_globals():
        unread_notifications = 0
        if current_user.is_authenticated:
            unread_notifications = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return dict(
            unread_notifications=unread_notifications,
            current_year=datetime.utcnow().year
        )

    return app


def _seed_initial_data():
    """Seed initial companies and admin user."""
    # Admin user
    if not User.query.filter_by(email='admin@placementai.com').first():
        admin = User(email='admin@placementai.com', role='admin', is_verified=True)
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()

        profile = StudentProfile(user_id=admin.id, full_name='CareerLens-AI Admin',
                                 college='CareerLens-AI HQ', department='Administration')
        db.session.add(profile)
        db.session.commit()
        print("[Seed] Admin user created: admin@placementai.com / Admin@123")

    # Demo student
    if not User.query.filter_by(email='student@demo.com').first():
        student = User(email='student@demo.com', role='student', is_verified=True)
        student.set_password('Student@123')
        db.session.add(student)
        db.session.commit()

        profile = StudentProfile(
            user_id=student.id, full_name='Priya Sharma',
            phone='+91-9876543210', college='IIT Bombay',
            department='Computer Science', year=3,
            bio='Passionate developer & ML enthusiast.',
            linkedin='https://linkedin.com/in/priyasharma',
            github='https://github.com/priyasharma',
            leetcode='https://leetcode.com/priyasharma',
            profile_completeness=85.0, daily_streak=12
        )
        db.session.add(profile)
        db.session.commit()

        edu = Education(profile_id=profile.id, cgpa=8.5, tenth_percent=92.0,
                        twelfth_percent=88.0, current_sem_percent=86.0,
                        backlogs=0, attendance=92.0, semester=6)
        skills = Skills(profile_id=profile.id, technical_score=8.0, communication_score=7.5,
                        aptitude_score=8.2, leadership_score=7.0, programming_score=8.5,
                        logical_reasoning=8.0, problem_solving=8.3, soft_skills=7.5,
                        interview_score=7.8, leetcode_solved=245, github_activity=7.5,
                        coding_contest_rating=1620, hackathons_participated=3)
        db.session.add_all([edu, skills])
        db.session.commit()

        # Sample projects
        projects = [
            Project(profile_id=profile.id, title='AI Resume Builder',
                    description='Automated resume generation using NLP and Gemini API.',
                    tech_stack='Python, Flask, React, Gemini API',
                    github_link='https://github.com/priya/resume-builder', difficulty='hard'),
            Project(profile_id=profile.id, title='E-Commerce Platform',
                    description='Full-stack e-commerce with payment integration.',
                    tech_stack='Next.js, Node.js, PostgreSQL, Stripe',
                    github_link='https://github.com/priya/ecommerce', difficulty='medium'),
            Project(profile_id=profile.id, title='IoT Smart Home System',
                    description='Raspberry Pi-based home automation system.',
                    tech_stack='Python, MQTT, React Native, AWS IoT',
                    github_link='https://github.com/priya/smarthome', difficulty='hard'),
        ]
        internships = [
            Internship(profile_id=profile.id, company='Google', role='SWE Intern',
                       duration_months=3, skills_gained='Python, Kubernetes, GCP',
                       stipend=80000, is_paid=True),
            Internship(profile_id=profile.id, company='Flipkart', role='Data Science Intern',
                       duration_months=2, skills_gained='ML, Pandas, SQL',
                       stipend=50000, is_paid=True),
        ]
        certs = [
            Certificate(profile_id=profile.id, title='AWS Cloud Practitioner',
                        issuer='Amazon Web Services', category='technical', score_impact=2.5),
            Certificate(profile_id=profile.id, title='Google Data Analytics',
                        issuer='Google', category='technical', score_impact=2.0),
            Certificate(profile_id=profile.id, title='Deep Learning Specialization',
                        issuer='Coursera/DeepLearning.AI', category='technical', score_impact=3.0),
        ]
        goals = [
            Goal(user_id=student.id, title='Solve 5 LeetCode Problems',
                 type='daily', progress=60, target=100),
            Goal(user_id=student.id, title='Complete System Design Course',
                 type='weekly', progress=40, target=100),
            Goal(user_id=student.id, title='Build Portfolio Project',
                 type='monthly', progress=75, target=100),
        ]
        notifications = [
            Notification(user_id=student.id, title='Profile 85% Complete!',
                         message='Add your resume to boost your prediction score.',
                         type='info'),
            Notification(user_id=student.id, title='New Interview Tip Available',
                         message='Check out our latest FAANG interview preparation guide.',
                         type='success'),
        ]
        db.session.add_all(projects + internships + certs + goals + notifications)
        db.session.commit()
        print("[Seed] Demo student created: student@demo.com / Student@123")

    # Companies
    if not Company.query.first():
        companies = [
            Company(name='Google', min_cgpa=7.5, package_lpa=45.0, max_backlogs=0,
                    required_skills=json.dumps(['Python', 'Algorithms', 'System Design']),
                    description='World leader in search and cloud technology.'),
            Company(name='Microsoft', min_cgpa=7.0, package_lpa=42.0, max_backlogs=0,
                    required_skills=json.dumps(['C++', 'Azure', 'Problem Solving']),
                    description='Enterprise software and cloud computing giant.'),
            Company(name='Amazon', min_cgpa=7.0, package_lpa=40.0, max_backlogs=0,
                    required_skills=json.dumps(['Java', 'AWS', 'Leadership Principles']),
                    description='E-commerce and cloud services leader.'),
            Company(name='TCS', min_cgpa=6.0, package_lpa=7.0, max_backlogs=2,
                    required_skills=json.dumps(['Communication', 'Aptitude', 'Any Language']),
                    description='India\'s largest IT services company.'),
            Company(name='Infosys', min_cgpa=6.5, package_lpa=8.0, max_backlogs=1,
                    required_skills=json.dumps(['Communication', 'Aptitude', 'Java']),
                    description='Global leader in next-generation digital services.'),
            Company(name='Wipro', min_cgpa=6.0, package_lpa=6.5, max_backlogs=2,
                    required_skills=json.dumps(['Communication', 'Aptitude', 'Any Language']),
                    description='Leading global IT, consulting, and business solutions.'),
            Company(name='Zoho', min_cgpa=6.5, package_lpa=12.0, max_backlogs=0,
                    required_skills=json.dumps(['Python', 'Java', 'Problem Solving', 'Communication']),
                    description='Product-based company known for quality products.'),
            Company(name='Accenture', min_cgpa=6.0, package_lpa=9.0, max_backlogs=2,
                    required_skills=json.dumps(['Communication', 'Adaptability', 'Technical Basics']),
                    description='Global consulting and technology services.'),
            Company(name='IBM', min_cgpa=6.5, package_lpa=10.0, max_backlogs=1,
                    required_skills=json.dumps(['Cloud', 'AI', 'Communication']),
                    description='Technology and consulting with AI focus.'),
            Company(name='Oracle', min_cgpa=7.0, package_lpa=22.0, max_backlogs=0,
                    required_skills=json.dumps(['Java', 'SQL', 'Algorithms']),
                    description='Enterprise software and database solutions.'),
        ]
        db.session.add_all(companies)
        db.session.commit()
        print("[Seed] Companies seeded.")

        students_data = [
            ("Rahul Verma", "rahul.verma@example.com", "Computer Science", "IIT Bombay", 96.0, 98.0, "3m 45s", 295.0, "11m 20s"),
            ("Ananya Iyer", "ananya.iyer@example.com", "Information Technology", "BITS Pilani", 95.0, 96.0, "3m 52s", 290.0, "11m 45s"),
            ("Priya Sharma", "priya.sharma@example.com", "Computer Science", "IIT Bombay", 92.0, 95.0, "4m 05s", 285.0, "12m 10s"),
            ("Rohan Gupta", "rohan.gupta@example.com", "Artificial Intelligence", "IIIT Hyderabad", 91.0, 93.0, "4m 15s", 280.0, "12m 35s"),
            ("Sneha Patel", "sneha.patel@example.com", "Data Science", "NIT Trichy", 90.0, 91.0, "4m 22s", 276.0, "12m 50s"),
            ("Aditya Nair", "aditya.nair@example.com", "Electronics", "College of Engg Guindy", 89.0, 90.0, "4m 30s", 272.0, "13m 05s"),
            ("Kavya Reddy", "kavya.reddy@example.com", "Computer Science", "VIT Vellore", 88.0, 88.0, "4m 40s", 268.0, "13m 20s"),
            ("Vikram Singh", "vikram.singh@example.com", "Information Technology", "DTU Delhi", 87.0, 87.0, "4m 48s", 265.0, "13m 40s"),
            ("Meera Joshi", "meera.joshi@example.com", "Data Science", "SRM Institute", 86.0, 85.0, "4m 55s", 260.0, "13m 55s"),
            ("Aman Khan", "aman.khan@example.com", "Computer Science", "IIT Madras", 85.0, 84.0, "5m 02s", 255.0, "14m 10s"),
            ("Pooja Sundaram", "pooja.s@example.com", "Electrical & Electronics", "PSG Tech", 84.0, 82.0, "5m 12s", 250.0, "14m 25s"),
            ("Yash Deshmukh", "yash.d@example.com", "Artificial Intelligence", "COEP Pune", 83.0, 80.0, "5m 20s", 245.0, "14m 40s"),
            ("Riya Chakraborty", "riya.c@example.com", "Information Technology", "Jadavpur Univ", 82.0, 79.0, "5m 30s", 240.0, "14m 55s"),
            ("Harsh Vardhan", "harsh.v@example.com", "Mechanical Engineering", "IIT Kharagpur", 81.0, 78.0, "5m 40s", 235.0, "15m 10s"),
            ("Divya Kulkarni", "divya.k@example.com", "Computer Science", "RVCE Bangalore", 80.0, 76.0, "5m 50s", 230.0, "15m 25s"),
            ("Karthik Menon", "karthik.m@example.com", "Cyber Security", "Amrita University", 79.0, 75.0, "6m 00s", 225.0, "15m 40s"),
            ("Neha Bhatia", "neha.b@example.com", "Data Science", "Thapar Institute", 78.0, 73.0, "6m 08s", 220.0, "15m 55s"),
            ("Siddharth Das", "siddharth.d@example.com", "Computer Science", "NIT Surathkal", 77.0, 72.0, "6m 15s", 215.0, "16m 10s"),
            ("Tanvi Agarwal", "tanvi.a@example.com", "Information Technology", "IGDTUW Delhi", 76.0, 70.0, "6m 22s", 210.0, "16m 25s"),
            ("Varun Rao", "varun.r@example.com", "Electronics", "MIT Manipal", 75.0, 68.0, "6m 30s", 205.0, "16m 40s"),
            ("Ishita Saxena", "ishita.s@example.com", "Artificial Intelligence", "Banasthali Vidyapith", 74.0, 67.0, "6m 35s", 200.0, "16m 55s"),
            ("Devansh Kumar", "devansh.k@example.com", "Computer Science", "Jamia Millia", 73.0, 65.0, "6m 40s", 195.0, "17m 10s"),
            ("Anushree Roy", "anushree.r@example.com", "Software Engineering", "Heritage Kolkata", 72.0, 64.0, "6m 45s", 190.0, "17m 25s"),
            ("Nikhil Kapoor", "nikhil.k@example.com", "Information Technology", "PEC Chandigarh", 71.0, 63.0, "6m 50s", 185.0, "17m 40s"),
            ("Simran Mehta", "simran.m@example.com", "Data Science", "MS Ramaiah Bangalore", 70.0, 62.0, "6m 55s", 175.0, "18m 00s"),
        ]

        for rank_idx, (name, email, dept, college, score, d_score, d_time, w_score, w_time) in enumerate(students_data, start=1):
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email, role='student', is_verified=True)
                user.set_password('Student@123')
                db.session.add(user)
                db.session.commit()

            prof = StudentProfile.query.filter_by(user_id=user.id).first()
            if not prof:
                prof = StudentProfile(user_id=user.id, full_name=name, college=college, department=dept, year=3, profile_completeness=85.0)
                db.session.add(prof)
                db.session.commit()

            lb = Leaderboard.query.filter_by(user_id=user.id).first()
            if not lb:
                lb = Leaderboard(
                    user_id=user.id, score=score, rank=rank_idx, department=dept, college=college,
                    daily_quiz_score=d_score, daily_quiz_rank=rank_idx, daily_quiz_time=d_time,
                    weekly_quiz_score=w_score, weekly_quiz_rank=rank_idx, weekly_quiz_time=w_time
                )
                db.session.add(lb)
            else:
                lb.score = score
                lb.rank = rank_idx
                lb.department = dept
                lb.college = college
                lb.daily_quiz_score = d_score
                lb.daily_quiz_rank = rank_idx
                lb.daily_quiz_time = d_time
                lb.weekly_quiz_score = w_score
                lb.weekly_quiz_rank = rank_idx
                lb.weekly_quiz_time = w_time

        db.session.commit()
        print("[Seed] 25 Leaderboard students with Daily & Weekly Quiz marks seeded.")


if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        db.create_all()
        _seed_initial_data()
    app.run(debug=True, port=5000, use_reloader=False)
