import os
import json

try:
    import numpy as np
except Exception:
    np = None

try:
    import joblib
except Exception:
    joblib = None

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline
except Exception:
    GradientBoostingClassifier = None

# ─── Model Path ──────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'placement_model.pkl')

# ─── Feature Names ───────────────────────────────────────────────────────────
FEATURE_NAMES = [
    'cgpa', 'tenth_percent', 'twelfth_percent', 'current_sem_percent',
    'communication_score', 'technical_score', 'programming_score',
    'aptitude_score', 'logical_reasoning', 'problem_solving',
    'leadership_score', 'soft_skills', 'interview_score',
    'projects_count', 'internships_count', 'hackathons_count',
    'certificates_count', 'leetcode_solved', 'github_activity',
    'attendance', 'backlogs', 'coding_contest_rating',
]

def create_and_train_model():
    """Create and train the ML model with synthetic data."""
    if np is None or GradientBoostingClassifier is None:
        return None
    try:
        np.random.seed(42)
        n_samples = 2000

        data = []
        labels = []
        for _ in range(n_samples):
            cgpa = np.random.uniform(4.0, 10.0)
            tenth = np.random.uniform(50, 100)
            twelfth = np.random.uniform(50, 100)
            sem_percent = np.random.uniform(50, 100)
            comm = np.random.uniform(1, 10)
            tech = np.random.uniform(1, 10)
            prog = np.random.uniform(1, 10)
            apt = np.random.uniform(1, 10)
            logic = np.random.uniform(1, 10)
            prob_solving = np.random.uniform(1, 10)
            leadership = np.random.uniform(1, 10)
            soft = np.random.uniform(1, 10)
            interview = np.random.uniform(1, 10)
            projects = np.random.randint(0, 10)
            internships = np.random.randint(0, 5)
            hackathons = np.random.randint(0, 8)
            certs = np.random.randint(0, 15)
            leetcode = np.random.randint(0, 500)
            github = np.random.uniform(0, 10)
            attendance = np.random.uniform(50, 100)
            backlogs = np.random.randint(0, 8)
            rating = np.random.randint(0, 3000)

            sample = [cgpa, tenth, twelfth, sem_percent, comm, tech, prog, apt,
                      logic, prob_solving, leadership, soft, interview,
                      projects, internships, hackathons, certs, leetcode,
                      github, attendance, backlogs, rating]
            data.append(sample)

            score = (
                cgpa * 0.25 + (tenth / 10) * 0.05 + (twelfth / 10) * 0.05 +
                (sem_percent / 10) * 0.10 + comm * 0.10 + tech * 0.15 +
                prog * 0.12 + apt * 0.08 + logic * 0.05 + interview * 0.10 +
                (projects * 0.5) + (internships * 0.8) - (backlogs * 0.5)
            )
            placed = 1 if (score + np.random.normal(0, 0.5)) > 7.5 else 0
            labels.append(placed)

        X = np.array(data)
        y = np.array(labels)

        model = Pipeline([
            ('scaler', StandardScaler()),
            ('clf', GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42))
        ])
        model.fit(X, y)
        if joblib:
            joblib.dump(model, MODEL_PATH)
        return model
    except Exception as e:
        print(f"[ML] Training fallback: {e}")
        return None

def load_model():
    """Load the model safely."""
    try:
        if os.path.exists(MODEL_PATH) and joblib:
            return joblib.load(MODEL_PATH)
        return create_and_train_model()
    except Exception as e:
        print(f"[ML] Load model notice: {e}")
        return None

_model = None

def get_model():
    global _model
    if _model is None:
        _model = load_model()
    return _model

def predict_placement(features: dict) -> dict:
    """Predict placement probability from feature dictionary."""
    def safe_get(key, default=0.0):
        val = features.get(key, default)
        return float(val) if val is not None else default

    cgpa = safe_get('cgpa', 7.0)
    tech = safe_get('technical_score', 5.0)
    comm = safe_get('communication_score', 5.0)
    prog = safe_get('programming_score', 5.0)
    apt = safe_get('aptitude_score', 5.0)
    interview = safe_get('interview_score', 5.0)
    leetcode = safe_get('leetcode_solved', 0)
    projects = safe_get('projects_count', 0)

    placement_score = (
        (cgpa / 10) * 25 +
        (tech / 10) * 20 +
        (comm / 10) * 15 +
        (prog / 10) * 15 +
        (apt / 10) * 10 +
        (interview / 10) * 10 +
        min(leetcode / 300, 1) * 5
    )

    model = get_model()
    probability = None
    if model is not None and np is not None:
        try:
            feature_vector = np.array([[
                cgpa, safe_get('tenth_percent', 75.0), safe_get('twelfth_percent', 75.0),
                safe_get('current_sem_percent', 75.0), comm, tech, prog, apt,
                safe_get('logical_reasoning', 5.0), safe_get('problem_solving', 5.0),
                safe_get('leadership_score', 5.0), safe_get('soft_skills', 5.0), interview,
                projects, safe_get('internships_count', 0), safe_get('hackathons_count', 0),
                safe_get('certificates_count', 0), leetcode, safe_get('github_activity', 0.0),
                safe_get('attendance', 75.0), safe_get('backlogs', 0), safe_get('coding_contest_rating', 0)
            ]])
            probability = float(model.predict_proba(feature_vector)[0][1]) * 100
        except Exception as e:
            print(f"[ML Predict Error] {e}")

    if probability is None:
        probability = min(max(placement_score * 1.15, 15.0), 98.0)

    result = "Placed" if probability >= 50 else "Not Placed"
    confidence = abs(probability - 50) * 2  # 0-100%

    # Calculate placement score (weighted composite)
    cgpa = safe_get('cgpa', 7.0)
    tech = safe_get('technical_score', 5.0)
    comm = safe_get('communication_score', 5.0)
    prog = safe_get('programming_score', 5.0)
    apt = safe_get('aptitude_score', 5.0)
    interview = safe_get('interview_score', 5.0)
    leetcode = safe_get('leetcode_solved', 0)
    projects = safe_get('projects_count', 0)

    placement_score = (
        (cgpa / 10) * 25 +
        (tech / 10) * 20 +
        (comm / 10) * 15 +
        (prog / 10) * 15 +
        (apt / 10) * 10 +
        (interview / 10) * 10 +
        min(leetcode / 300, 1) * 5
    )

    # Determine strengths and weaknesses
    scores_map = {
        'CGPA': (cgpa / 10) * 10,
        'Technical Skills': tech,
        'Communication': comm,
        'Programming': prog,
        'Aptitude': apt,
        'Interview Readiness': interview,
        'Problem Solving': safe_get('problem_solving', 5.0),
        'Leadership': safe_get('leadership_score', 5.0),
    }

    sorted_scores = sorted(scores_map.items(), key=lambda x: x[1], reverse=True)
    strengths = [f"{k} ({v:.1f}/10)" for k, v in sorted_scores[:3] if v >= 6]
    weaknesses = [f"{k} ({v:.1f}/10)" for k, v in sorted_scores[-3:] if v < 7]

    # Generate suggestions
    suggestions = []
    if safe_get('cgpa', 7.0) < 7.0:
        suggestions.append("Improve your CGPA to at least 7.0 for better company eligibility.")
    if safe_get('leetcode_solved', 0) < 100:
        suggestions.append("Solve at least 100 LeetCode problems to strengthen DSA skills.")
    if safe_get('projects_count', 0) < 3:
        suggestions.append("Build 2-3 real-world projects to demonstrate practical skills.")
    if safe_get('communication_score', 5.0) < 7.0:
        suggestions.append("Practice English communication and group discussions daily.")
    if safe_get('internships_count', 0) < 1:
        suggestions.append("Complete at least one internship for industry exposure.")
    if safe_get('backlogs', 0) > 0:
        suggestions.append("Clear all academic backlogs before placement season.")
    if safe_get('github_activity', 0) < 3.0:
        suggestions.append("Maintain active GitHub contributions (aim for daily commits).")
    if safe_get('certificates_count', 0) < 3:
        suggestions.append("Earn 3+ recognized certifications (AWS, Google, Coursera).")

    if not suggestions:
        suggestions.append("You are well-prepared! Keep refining your interview skills.")

    return {
        'probability': round(probability, 2),
        'result': result,
        'confidence': round(min(confidence, 100), 2),
        'placement_score': round(placement_score, 2),
        'strengths': strengths,
        'weaknesses': weaknesses,
        'suggestions': suggestions,
    }


def calculate_readiness_score(features: dict) -> dict:
    """Calculate detailed readiness breakdown."""
    def safe_get(key, default=0.0):
        val = features.get(key, default)
        return float(val) if val is not None else default

    skill_score = (
        safe_get('technical_score', 0) * 0.35 +
        safe_get('programming_score', 0) * 0.35 +
        safe_get('aptitude_score', 0) * 0.30
    ) * 10

    resume_score = safe_get('resume_score', 50)

    interview_score = (
        safe_get('interview_score', 0) * 0.5 +
        safe_get('communication_score', 0) * 0.3 +
        safe_get('leadership_score', 0) * 0.2
    ) * 10

    coding_score = min(
        (safe_get('leetcode_solved', 0) / 300) * 50 +
        (safe_get('github_activity', 0) / 10) * 30 +
        min(safe_get('projects_count', 0) / 5, 1) * 20,
        100
    )

    comm_score = (
        safe_get('communication_score', 0) * 0.5 +
        safe_get('soft_skills', 0) * 0.3 +
        safe_get('leadership_score', 0) * 0.2
    ) * 10

    overall = (skill_score * 0.3 + resume_score * 0.2 +
               interview_score * 0.2 + coding_score * 0.15 + comm_score * 0.15)

    return {
        'skill_score': round(skill_score, 1),
        'resume_score': round(resume_score, 1),
        'interview_score': round(interview_score, 1),
        'coding_score': round(coding_score, 1),
        'communication_score': round(comm_score, 1),
        'overall_score': round(overall, 1),
    }
