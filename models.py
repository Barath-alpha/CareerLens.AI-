from datetime import datetime
from extensions import db
from flask_login import UserMixin
import bcrypt


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default='student')  # student, admin
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_history = db.relationship('ChatHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<User {self.email}>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    college = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    photo_url = db.Column(db.String(500), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    linkedin = db.Column(db.String(300), nullable=True)
    github = db.Column(db.String(300), nullable=True)
    leetcode = db.Column(db.String(300), nullable=True)
    hackerrank = db.Column(db.String(300), nullable=True)
    portfolio = db.Column(db.String(300), nullable=True)
    codechef = db.Column(db.String(300), nullable=True)
    expected_salary = db.Column(db.Float, nullable=True)
    preferred_companies = db.Column(db.Text, nullable=True)
    profile_completeness = db.Column(db.Float, default=0.0)
    resume_url = db.Column(db.String(500), nullable=True)
    resume_score = db.Column(db.Float, nullable=True)
    daily_streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    education = db.relationship('Education', backref='profile', uselist=False, cascade='all, delete-orphan')
    skills = db.relationship('Skills', backref='profile', uselist=False, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='profile', lazy=True, cascade='all, delete-orphan')
    internships = db.relationship('Internship', backref='profile', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='profile', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='profile', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def calculate_completeness(self):
        fields = [self.full_name, self.phone, self.college, self.department,
                  self.year, self.bio, self.linkedin, self.github, self.resume_url]
        filled = sum(1 for f in fields if f)
        self.profile_completeness = (filled / len(fields)) * 100
        return self.profile_completeness

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'phone': self.phone,
            'college': self.college,
            'department': self.department,
            'year': self.year,
            'photo_url': self.photo_url,
            'bio': self.bio,
            'linkedin': self.linkedin,
            'github': self.github,
            'leetcode': self.leetcode,
            'hackerrank': self.hackerrank,
            'portfolio': self.portfolio,
            'resume_url': self.resume_url,
            'resume_score': self.resume_score,
            'profile_completeness': self.profile_completeness,
            'daily_streak': self.daily_streak,
            'expected_salary': self.expected_salary,
        }

    def __repr__(self):
        return f'<StudentProfile {self.full_name}>'


class Education(db.Model):
    __tablename__ = 'education'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), unique=True, nullable=False)
    cgpa = db.Column(db.Float, nullable=True)
    tenth_percent = db.Column(db.Float, nullable=True)
    twelfth_percent = db.Column(db.Float, nullable=True)
    current_sem_percent = db.Column(db.Float, nullable=True)
    backlogs = db.Column(db.Integer, default=0)
    attendance = db.Column(db.Float, nullable=True)
    semester = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'cgpa': self.cgpa,
            'tenth_percent': self.tenth_percent,
            'twelfth_percent': self.twelfth_percent,
            'current_sem_percent': self.current_sem_percent,
            'backlogs': self.backlogs,
            'attendance': self.attendance,
            'semester': self.semester,
        }


class Skills(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), unique=True, nullable=False)
    technical_score = db.Column(db.Float, default=0.0)
    communication_score = db.Column(db.Float, default=0.0)
    aptitude_score = db.Column(db.Float, default=0.0)
    leadership_score = db.Column(db.Float, default=0.0)
    programming_score = db.Column(db.Float, default=0.0)
    logical_reasoning = db.Column(db.Float, default=0.0)
    problem_solving = db.Column(db.Float, default=0.0)
    soft_skills = db.Column(db.Float, default=0.0)
    interview_score = db.Column(db.Float, default=0.0)
    leetcode_solved = db.Column(db.Integer, default=0)
    github_activity = db.Column(db.Float, default=0.0)
    coding_contest_rating = db.Column(db.Integer, default=0)
    hackathons_participated = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'technical_score': self.technical_score,
            'communication_score': self.communication_score,
            'aptitude_score': self.aptitude_score,
            'leadership_score': self.leadership_score,
            'programming_score': self.programming_score,
            'logical_reasoning': self.logical_reasoning,
            'problem_solving': self.problem_solving,
            'soft_skills': self.soft_skills,
            'interview_score': self.interview_score,
            'leetcode_solved': self.leetcode_solved,
            'github_activity': self.github_activity,
            'coding_contest_rating': self.coding_contest_rating,
            'hackathons_participated': self.hackathons_participated,
        }


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tech_stack = db.Column(db.String(500), nullable=True)
    github_link = db.Column(db.String(300), nullable=True)
    demo_link = db.Column(db.String(300), nullable=True)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'tech_stack': self.tech_stack,
            'github_link': self.github_link,
            'demo_link': self.demo_link,
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Internship(db.Model):
    __tablename__ = 'internships'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(150), nullable=True)
    duration_months = db.Column(db.Integer, nullable=True)
    skills_gained = db.Column(db.Text, nullable=True)
    stipend = db.Column(db.Float, nullable=True)
    is_paid = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    certificate_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'company': self.company,
            'role': self.role,
            'duration_months': self.duration_months,
            'skills_gained': self.skills_gained,
            'stipend': self.stipend,
            'is_paid': self.is_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(150), nullable=True)
    category = db.Column(db.String(100), nullable=True)  # technical, soft-skills, domain
    score_impact = db.Column(db.Float, default=0.0)
    certificate_url = db.Column(db.String(500), nullable=True)
    issued_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'issuer': self.issuer,
            'category': self.category,
            'score_impact': self.score_impact,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    result = db.Column(db.String(20), nullable=False)  # Placed / Not Placed
    confidence = db.Column(db.Float, nullable=True)
    placement_score = db.Column(db.Float, nullable=True)
    strengths = db.Column(db.Text, nullable=True)     # JSON string
    weaknesses = db.Column(db.Text, nullable=True)    # JSON string
    suggestions = db.Column(db.Text, nullable=True)   # JSON string
    ai_analysis = db.Column(db.Text, nullable=True)
    input_snapshot = db.Column(db.Text, nullable=True)  # JSON of features used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'probability': self.probability,
            'result': self.result,
            'confidence': self.confidence,
            'placement_score': self.placement_score,
            'strengths': json.loads(self.strengths) if self.strengths else [],
            'weaknesses': json.loads(self.weaknesses) if self.weaknesses else [],
            'suggestions': json.loads(self.suggestions) if self.suggestions else [],
            'ai_analysis': self.ai_analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), default='info')  # info, success, warning, alert
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    progress = db.Column(db.Float, default=0.0)
    target = db.Column(db.Float, default=100.0)
    is_completed = db.Column(db.Boolean, default=False)
    target_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'progress': self.progress,
            'target': self.target,
            'is_completed': self.is_completed,
            'target_date': self.target_date.isoformat() if self.target_date else None,
        }


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    badge_icon = db.Column(db.String(100), nullable=True)
    badge_color = db.Column(db.String(20), default='gold')
    points = db.Column(db.Integer, default=0)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'badge_icon': self.badge_icon,
            'badge_color': self.badge_color,
            'points': self.points,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
        }


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    logo_url = db.Column(db.String(500), nullable=True)
    min_cgpa = db.Column(db.Float, default=6.0)
    required_skills = db.Column(db.Text, nullable=True)  # JSON
    package_lpa = db.Column(db.Float, nullable=True)
    max_backlogs = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(300), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'name': self.name,
            'logo_url': self.logo_url,
            'min_cgpa': self.min_cgpa,
            'required_skills': json.loads(self.required_skills) if self.required_skills else [],
            'package_lpa': self.package_lpa,
            'max_backlogs': self.max_backlogs,
            'description': self.description,
            'website': self.website,
        }


class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    score = db.Column(db.Float, default=0.0)
    rank = db.Column(db.Integer, nullable=True)
    department = db.Column(db.String(100), nullable=True)
    college = db.Column(db.String(200), nullable=True)
    week_score = db.Column(db.Float, default=0.0)
    month_score = db.Column(db.Float, default=0.0)
    daily_quiz_score = db.Column(db.Float, default=0.0)
    daily_quiz_rank = db.Column(db.Integer, nullable=True)
    daily_quiz_time = db.Column(db.String(50), default='5m 00s')
    weekly_quiz_score = db.Column(db.Float, default=0.0)
    weekly_quiz_rank = db.Column(db.Integer, nullable=True)
    weekly_quiz_time = db.Column(db.String(50), default='15m 00s')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'score': self.score,
            'rank': self.rank,
            'department': self.department,
            'week_score': self.week_score,
            'month_score': self.month_score,
        }


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
