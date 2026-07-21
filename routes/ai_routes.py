import os
import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import ChatHistory, StudentProfile, Education, Skills, Project, Internship, Certificate

ai_bp = Blueprint('ai', __name__)


def call_gemini(prompt: str, system_prompt: str = None) -> str:
    """Call Gemini API or return a smart fallback."""
    api_key = os.environ.get('GEMINI_API_KEY', '')

    if api_key and api_key != 'your-gemini-api-key-here':
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"[Gemini Error] {e}")

    # Intelligent fallback responses
    return _smart_fallback(prompt)


def _smart_fallback(prompt: str) -> str:
    """Provide intelligent fallback responses without API."""
    prompt_lower = prompt.lower()

    if any(w in prompt_lower for w in ['interview', 'question', 'prepare']):
        return """Here are key interview preparation tips:

**Technical Interview:**
• Master Data Structures & Algorithms (Arrays, Trees, Graphs, DP)
• Practice on LeetCode - aim for 200+ problems across Easy/Medium/Hard
• Study System Design fundamentals (Load Balancing, Caching, Databases)
• Know your projects inside-out - be ready to explain every line

**HR Interview:**
• Practice STAR method (Situation, Task, Action, Result) for behavioral questions
• Research the company's products, culture, and recent news
• Prepare answers for: "Tell me about yourself", "Why this company?", "5-year plan"
• Have 3-5 thoughtful questions ready to ask the interviewer

**Common Questions to Master:**
1. Explain a challenging project you built
2. How do you handle conflicts in a team?
3. What's your greatest weakness?
4. Walk me through your resume

**Day Before:**
• Good sleep (8 hours minimum)
• Prepare your outfit and documents
• Review your projects one more time
• Practice deep breathing for confidence"""

    elif any(w in prompt_lower for w in ['resume', 'cv', 'ats']):
        return """**Resume Optimization Guide:**

**ATS-Friendly Tips:**
• Use standard section headers: Education, Experience, Projects, Skills
• Include keywords from the job description
• Use simple formatting - no tables, no graphics, no headers/footers
• File format: PDF for human review, .docx for ATS parsing

**Content Best Practices:**
• Lead with a strong 2-3 line summary/objective
• Quantify achievements: "Increased performance by 40%" not "improved performance"
• Use action verbs: Built, Developed, Designed, Led, Optimized, Reduced
• List technologies used in each project

**Structure (1 page for freshers):**
1. Contact Info + LinkedIn + GitHub
2. Skills Section (prominently placed)
3. Education (with CGPA if >7.5)
4. Projects (3-4 strong projects)
5. Internships/Experience
6. Certifications & Achievements

**Red Flags to Avoid:**
• Typos and grammatical errors
• Generic objective statements
• Listing skills you can't defend in interview
• Including irrelevant school activities"""

    elif any(w in prompt_lower for w in ['roadmap', 'learn', 'skill', 'course']):
        return """**Personalized Learning Roadmap for Placement:**

**Month 1-2: Foundation**
• DSA: Arrays, Strings, Recursion (LeetCode Easy - 50 problems)
• Language mastery: Python/Java/C++ - pick one and go deep
• Git & GitHub: Make daily contributions visible
• Coursera: "Python for Everybody" or equivalent

**Month 3-4: Intermediate**
• DSA: Trees, Graphs, Dynamic Programming (LeetCode Medium - 80 problems)
• Build Project 1: Full-stack web app with CRUD operations
• Database: SQL fundamentals (MySQL/PostgreSQL)
• Complete: Google Data Analytics or AWS Cloud Practitioner

**Month 5-6: Advanced + Placement Prep**
• DSA: Advanced graphs, System Design basics (LeetCode Hard - 30 problems)
• Build Project 2: ML/AI integrated application
• Mock interviews: Pramp, Interviewing.io
• Resume finalization + LinkedIn optimization

**Top Free Resources:**
• CS50 (Harvard) - YouTube
• NeetCode roadmap - neetcode.io
• System Design Primer - GitHub
• freeCodeCamp - Full courses

**Certifications Worth Getting:**
• AWS Cloud Practitioner (₹8,000 exam)
• Google Professional Certificates (Free via Financial Aid)
• Meta Front-End Developer Certificate"""

    elif any(w in prompt_lower for w in ['salary', 'package', 'company', 'tier']):
        return """**Company Tiers & Expected Packages (2024-25):**

**Tier 1 (Product Companies) - ₹30-60+ LPA:**
• Google, Microsoft, Amazon, Apple, Meta
• Requirements: 8+ CGPA, 300+ LeetCode, Strong DSA & System Design

**Tier 2 (Good Product Companies) - ₹15-30 LPA:**
• Zoho, Freshworks, Swiggy, Zepto, Razorpay, Atlassian
• Requirements: 7+ CGPA, 150+ LeetCode, 2-3 strong projects

**Tier 3 (Service Companies) - ₹6-12 LPA:**
• TCS, Infosys, Wipro, Accenture, Cognizant
• Requirements: 6+ CGPA, basic programming, good communication

**Tier 4 (MNCs + Consulting) - ₹10-20 LPA:**
• IBM, Oracle, Capgemini, Deloitte
• Requirements: 7+ CGPA, domain knowledge, communication

**Strategy:**
• Apply to all tiers simultaneously
• Start with Tier 3 to build confidence
• Prepare specifically for each company's known process
• Get referrals through LinkedIn connections"""

    else:
        return f"""I'm CareerLens-AI's Career Advisor! 🎓

I can help you with:
• **Interview Preparation** - Technical & HR tips, mock questions
• **Resume Building** - ATS optimization, content guidelines  
• **Learning Roadmap** - Personalized study plan for placement
• **Company Research** - Salary expectations, requirements by tier
• **Skill Assessment** - Understanding your strengths & gaps
• **Project Ideas** - Resume-worthy project suggestions
• **Career Guidance** - Which roles suit your profile

What would you like help with today? Ask me anything about your placement journey! 💪

*Tip: The more specific your question, the more tailored my advice will be.*"""


@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'success': False, 'message': 'Message cannot be empty'}), 400

    # Get user context
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    education = Education.query.filter_by(profile_id=profile.id).first() if profile else None
    skills = Skills.query.filter_by(profile_id=profile.id).first() if profile else None

    system_prompt = f"""You are CareerLens-AI's Career Advisor, an expert AI assistant helping college students prepare for campus placements. 

Student Context:
- Name: {profile.full_name if profile else 'Student'}
- College: {profile.college if profile else 'Unknown'}
- Department: {profile.department if profile else 'Unknown'}
- Year: {profile.year if profile else 'Unknown'}
- CGPA: {education.cgpa if education else 'Not set'}
- Technical Score: {skills.technical_score if skills else 'Not assessed'}/10
- LeetCode Solved: {skills.leetcode_solved if skills else 0}

Be helpful, encouraging, and specific. Provide actionable advice with concrete steps. Use emojis sparingly for friendliness."""

    # Generate response
    ai_response = call_gemini(user_message, system_prompt)

    # Save to history
    user_msg = ChatHistory(user_id=current_user.id, role='user', message=user_message)
    ai_msg = ChatHistory(user_id=current_user.id, role='assistant', message=ai_response)
    db.session.add_all([user_msg, ai_msg])
    db.session.commit()

    return jsonify({'success': True, 'response': ai_response, 'message_id': ai_msg.id})


@ai_bp.route('/analyze-resume', methods=['POST'])
@login_required
def analyze_resume():
    """Analyze resume and return scores + suggestions."""
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    skills = Skills.query.filter_by(profile_id=profile.id).first() if profile else None
    education = Education.query.filter_by(profile_id=profile.id).first() if profile else None
    projects = Project.query.filter_by(profile_id=profile.id).all() if profile else []
    internships = Internship.query.filter_by(profile_id=profile.id).all() if profile else []
    certs = Certificate.query.filter_by(profile_id=profile.id).all() if profile else []

    # Calculate resume score based on profile completeness
    score = 0
    breakdown = {}
    suggestions = []

    # Contact & Summary (15 points)
    contact_score = 15 if (profile and profile.full_name and profile.phone and profile.linkedin) else 8
    breakdown['contact'] = contact_score
    if not (profile and profile.linkedin):
        suggestions.append("Add your LinkedIn profile URL to your resume.")

    # Education (20 points)
    if education and education.cgpa:
        edu_score = min(20, int((education.cgpa / 10) * 20))
        if education.cgpa < 7.0:
            suggestions.append("Consider highlighting relevant coursework since CGPA is below 7.0.")
    else:
        edu_score = 5
        suggestions.append("Add your CGPA and academic details to your resume.")
    breakdown['education'] = edu_score

    # Projects (25 points)
    proj_score = min(25, len(projects) * 8)
    breakdown['projects'] = proj_score
    if len(projects) < 3:
        suggestions.append(f"Add more projects ({3 - len(projects)} more recommended). Aim for 3-4 impactful projects.")
    if projects and not any(p.github_link for p in projects):
        suggestions.append("Add GitHub links to all your projects for ATS scanning.")

    # Experience (20 points)
    exp_score = min(20, len(internships) * 10)
    breakdown['experience'] = exp_score
    if len(internships) == 0:
        suggestions.append("Add any internships, freelance work, or open-source contributions.")

    # Skills (15 points)
    if skills and skills.technical_score > 0:
        skill_score = int((skills.technical_score / 10) * 15)
    else:
        skill_score = 5
        suggestions.append("List your technical skills explicitly (languages, frameworks, tools).")
    breakdown['skills'] = skill_score

    # Certifications (5 points)
    cert_score = min(5, len(certs) * 2)
    breakdown['certifications'] = cert_score
    if len(certs) < 2:
        suggestions.append("Add relevant certifications (AWS, Google, Coursera) to boost your score.")

    score = sum(breakdown.values())

    # Update profile
    if profile:
        profile.resume_score = score
        db.session.commit()

    # ATS tips
    ats_issues = []
    if score < 60:
        ats_issues.append("Resume may not pass ATS filters - add more keywords from job descriptions.")
    if not (profile and profile.github):
        ats_issues.append("Missing GitHub profile - important for technical roles.")

    return jsonify({
        'success': True,
        'score': score,
        'breakdown': breakdown,
        'suggestions': suggestions,
        'ats_issues': ats_issues,
        'grade': 'A' if score >= 85 else 'B' if score >= 70 else 'C' if score >= 55 else 'D'
    })


@ai_bp.route('/mock-interview', methods=['POST'])
@login_required
def mock_interview():
    data = request.get_json()
    interview_type = data.get('type', 'technical')  # technical, hr, behavioral
    domain = data.get('domain', 'software')

    system_prompt = f"""You are an expert interviewer conducting a {interview_type} interview for {domain} roles.
Generate a realistic interview question with:
1. The question itself
2. What the interviewer is looking for
3. Key points a good answer should cover
4. A sample strong answer
Keep it realistic and practical for campus placements."""

    prompt = f"Generate a {interview_type} interview question for a {domain} position at a top tech company."
    response = call_gemini(prompt, system_prompt)

    return jsonify({'success': True, 'question': response, 'type': interview_type})


@ai_bp.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    education = Education.query.filter_by(profile_id=profile.id).first() if profile else None
    skills = Skills.query.filter_by(profile_id=profile.id).first() if profile else None

    # Generate recommendations based on weak areas
    weak_areas = []
    if skills:
        scores = {
            'Technical Skills': skills.technical_score,
            'Communication': skills.communication_score,
            'Programming': skills.programming_score,
            'Aptitude': skills.aptitude_score,
            'Problem Solving': skills.problem_solving,
        }
        weak_areas = [k for k, v in scores.items() if v < 6.0]

    recommendations = []

    # Courses
    course_map = {
        'Technical Skills': [
            {'title': 'CS50: Introduction to Computer Science', 'platform': 'Harvard/edX', 'url': 'https://cs50.harvard.edu', 'type': 'course'},
            {'title': 'The Odin Project', 'platform': 'Free', 'url': 'https://theodinproject.com', 'type': 'course'},
        ],
        'Programming': [
            {'title': 'Python Bootcamp', 'platform': 'Udemy', 'url': 'https://udemy.com', 'type': 'course'},
            {'title': 'Competitive Programming', 'platform': 'Codeforces', 'url': 'https://codeforces.com', 'type': 'practice'},
        ],
        'Aptitude': [
            {'title': 'IndiaBIX Aptitude Practice', 'platform': 'IndiaBIX', 'url': 'https://indiabix.com', 'type': 'practice'},
            {'title': 'RS Aggarwal Quantitative Aptitude', 'platform': 'Books', 'url': '#', 'type': 'book'},
        ],
        'Communication': [
            {'title': 'Public Speaking Fundamentals', 'platform': 'Coursera', 'url': 'https://coursera.org', 'type': 'course'},
            {'title': 'English Communication Skills', 'platform': 'British Council', 'url': 'https://learnenglish.britishcouncil.org', 'type': 'course'},
        ],
    }

    # Always include DSA
    recommendations.append({
        'category': 'DSA & Problem Solving',
        'resources': [
            {'title': 'NeetCode 150 Roadmap', 'platform': 'NeetCode.io', 'url': 'https://neetcode.io', 'type': 'practice'},
            {'title': 'LeetCode Daily Challenge', 'platform': 'LeetCode', 'url': 'https://leetcode.com', 'type': 'practice'},
            {'title': 'Striver\'s SDE Sheet', 'platform': 'TakeUForward', 'url': 'https://takeuforward.org', 'type': 'practice'},
        ]
    })

    for area in weak_areas[:3]:
        if area in course_map:
            recommendations.append({'category': area, 'resources': course_map[area]})

    # Always add career
    recommendations.append({
        'category': 'Interview Preparation',
        'resources': [
            {'title': 'Pramp - Peer Mock Interviews', 'platform': 'Pramp', 'url': 'https://pramp.com', 'type': 'practice'},
            {'title': 'InterviewBit', 'platform': 'InterviewBit', 'url': 'https://interviewbit.com', 'type': 'practice'},
            {'title': 'System Design Primer', 'platform': 'GitHub', 'url': 'https://github.com/donnemartin/system-design-primer', 'type': 'resource'},
        ]
    })

    return jsonify({'success': True, 'recommendations': recommendations, 'weak_areas': weak_areas})


@ai_bp.route('/learning-path', methods=['GET'])
@login_required
def learning_path():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    education = Education.query.filter_by(profile_id=profile.id).first() if profile else None
    skills = Skills.query.filter_by(profile_id=profile.id).first() if profile else None

    prompt = f"""Create a personalized 3-month placement preparation learning path for:
- Department: {profile.department if profile else 'Computer Science'}
- Year: {profile.year if profile else 3}
- CGPA: {education.cgpa if education else 7.0}
- Current Technical Score: {skills.technical_score if skills else 5}/10
- LeetCode Problems: {skills.leetcode_solved if skills else 0}

Format as a structured weekly plan with specific goals and resources."""

    response = call_gemini(prompt)
    return jsonify({'success': True, 'learning_path': response})


from interview_questions_data import get_questions

@ai_bp.route('/interview-questions', methods=['POST'])
@login_required
def interview_questions():
    data = request.get_json() or {}
    q_type = data.get('type', 'technical')
    company = data.get('company', '')
    difficulty = data.get('difficulty', 'medium')
    count = int(data.get('count', 10))

    selected = get_questions(q_type=q_type, difficulty=difficulty, count=count, company=company)

    return jsonify({
        'success': True,
        'questions': selected,
        'type': q_type.capitalize(),
        'difficulty': difficulty,
        'company': company
    })
