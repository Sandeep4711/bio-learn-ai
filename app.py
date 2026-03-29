from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
import os, cohere, json, datetime

# Initialize environment and app
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or os.urandom(32)

# Database Configuration (Root Directory)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# OAuth Configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# AI Engine Initialization
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY) if COHERE_API_KEY else None

# --- DATABASE MODELS ---

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=True)
    password = db.Column(db.String(150), nullable=True)  # Nullable for OAuth users
    google_id = db.Column(db.String(200), unique=True, nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)

    # Personal Information
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)  # Male, Female, Other, Prefer not to say
    qualification = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    university = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    results = db.relationship('QuizResult', backref='user', lazy=True)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200))
    score = db.Column(db.Integer)
    total = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # Timestamp of quiz completion
    date_only = db.Column(db.Date, nullable=False)  # Just the date for grouping
    time_only = db.Column(db.Time, nullable=False)  # Just the time for display
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class LearnerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    education_level = db.Column(db.String(50), default='undergraduate')  # school/undergraduate/postgraduate
    knowledge_level = db.Column(db.String(50), default='beginner')  # beginner/intermediate/advanced
    learning_style = db.Column(db.String(50), default='mixed')  # visual/text/interactive/mixed
    study_hours_per_week = db.Column(db.Integer, default=10)
    learning_goal = db.Column(db.String(100), default='general understanding')
    target_duration_weeks = db.Column(db.Integer, default=12)
    completed_topics = db.Column(db.JSON, default=list)
    weak_areas = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref='learner_profile')

class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('learner_profile.id'), nullable=False)
    path_data = db.Column(db.JSON, nullable=False)
    weekly_plan = db.Column(db.JSON, nullable=False)
    progression_strategy = db.Column(db.JSON, nullable=False)
    motivation_tips = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user = db.relationship('User', backref='learning_paths')
    profile = db.relationship('LearnerProfile', backref='learning_paths')

class StudyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # Date of study
    start_time = db.Column(db.Time, nullable=True)  # When study session started
    end_time = db.Column(db.Time, nullable=True)  # When study session ended
    study_time_minutes = db.Column(db.Integer, default=0)
    topics_covered = db.Column(db.JSON, default=list)
    subtopics = db.Column(db.JSON, default=list)
    learning_activities = db.Column(db.JSON, default=list)  # video, reading, quiz, lab_simulation
    quiz_score = db.Column(db.Float, nullable=True)
    focus_level = db.Column(db.String(20), default='medium')  # low, medium, high
    feedback = db.Column(db.Text, nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)  # When logged to system
    user = db.relationship('User', backref='study_logs')

class LessonHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(50), nullable=False)  # High School, Undergraduate, Graduate
    content = db.Column(db.Text, nullable=False)  # The generated lesson content
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref='lesson_history')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- PRESENTATION & AUTH ROUTES ---

@app.route('/')
def welcome():
    """Project Launch Page & Presentation View"""
    return render_template('welcome.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if user exists
        stmt = select(User).filter_by(username=username)
        if db.session.execute(stmt).scalar_one_or_none():
            flash('Researcher ID already exists in the registry!')
            return redirect(url_for('signup'))
        
        # Create new researcher profile
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        stmt = select(User).filter_by(username=username)
        user = db.session.execute(stmt).scalar_one_or_none()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('terminal'))
        
        flash('Access Denied: Invalid Researcher Credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('welcome'))

# --- GOOGLE OAUTH ROUTES ---

@app.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            flash('Failed to get user information from Google')
            return redirect(url_for('login'))

        # Check if user exists by Google ID
        stmt = select(User).filter_by(google_id=user_info['sub'])
        user = db.session.execute(stmt).scalar_one_or_none()

        if not user:
            # Check if user exists by email
            stmt = select(User).filter_by(email=user_info['email'])
            user = db.session.execute(stmt).scalar_one_or_none()

            if user:
                # Link existing account with Google
                user.google_id = user_info['sub']
                user.profile_picture = user_info.get('picture')
            else:
                # Create new user
                username = user_info['email'].split('@')[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while db.session.execute(select(User).filter_by(username=username)).scalar_one_or_none():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=user_info['email'],
                    google_id=user_info['sub'],
                    profile_picture=user_info.get('picture')
                )
                db.session.add(user)

            db.session.commit()

        login_user(user)
        return redirect(url_for('terminal'))

    except Exception as e:
        print(f"OAuth Error: {e}")
        flash('Authentication failed. Please try again.')
        return redirect(url_for('login'))

# --- CORE RESEARCH TERMINAL (Protected) ---

@app.route('/terminal')
@login_required
def terminal():
    """Main Research Dashboard"""
    return render_template('index.html')

@app.route('/module')
@login_required
def module_view():
    """AI Generated Content Viewer"""
    return render_template('module.html')

@app.route('/quiz')
@login_required
def quiz_view():
    """Dynamic Assessment Interface"""
    return render_template('quiz.html')

@app.route('/analytics')
@login_required
def analytics_view():
    """User Mastery & Data Visuals"""
    # Get the latest quiz result for each topic (not all attempts)
    from sqlalchemy import func

    # Subquery to get the max date for each topic
    latest_dates = (
        db.session.query(
            QuizResult.topic,
            func.max(QuizResult.date).label('max_date')
        )
        .filter_by(user_id=current_user.id)
        .group_by(QuizResult.topic)
        .subquery()
    )

    # Join to get the latest quiz result for each topic
    stmt = (
        select(QuizResult)
        .join(
            latest_dates,
            (QuizResult.topic == latest_dates.c.topic) &
            (QuizResult.date == latest_dates.c.max_date) &
            (QuizResult.user_id == current_user.id)
        )
        .order_by(QuizResult.date.desc())
    )

    history = db.session.execute(stmt).scalars().all()
    return render_template('analytics.html', history=history)

# --- AI & DATA ENDPOINTS ---

@app.route('/api/generate-topic', methods=['POST'])
@login_required
def generate_topic():
    data = request.json
    topic = data.get('topic')
    level = data.get('level', 'Undergraduate')  # Get complexity level

    # Advanced professor prompt for module generation
    message = (
        f"Act as a World-Class Biotechnology Professor. Create a detailed {level}-level "
        f"self-learning module on the topic: {topic}. "
        "Include clear sections for Introduction, Biological Mechanisms, and Industry Applications."
    )

    if co is None:
        return jsonify({"error": "AI engine is not configured on the server"}), 500

    try:
        response = co.chat(model='command-a-03-2025', message=message)

        # Save to lesson history
        lesson_history = LessonHistory(
            user_id=current_user.id,
            topic=topic,
            level=level,
            content=response.text
        )
        db.session.add(lesson_history)
        db.session.commit()

        return jsonify({
            "content": response.text,
            "topic": topic,
            "lesson_id": lesson_history.id,
            "reset_current": True  # Signal frontend to clear localStorage
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lesson-history', methods=['GET'])
@login_required
def get_lesson_history():
    """Get all lesson history for the current user"""
    try:
        stmt = select(LessonHistory).filter_by(user_id=current_user.id).order_by(LessonHistory.created_at.desc())
        lessons = db.session.execute(stmt).scalars().all()

        lesson_list = []
        for lesson in lessons:
            lesson_list.append({
                "id": lesson.id,
                "topic": lesson.topic,
                "level": lesson.level,
                "content": lesson.content,
                "created_at": lesson.created_at.strftime("%b %d, %Y at %I:%M %p")
            })

        return jsonify({"lessons": lesson_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lesson-history/<int:lesson_id>', methods=['GET'])
@login_required
def get_lesson_by_id(lesson_id):
    """Get a specific lesson by ID"""
    try:
        stmt = select(LessonHistory).filter_by(id=lesson_id, user_id=current_user.id)
        lesson = db.session.execute(stmt).scalar_one_or_none()

        if not lesson:
            return jsonify({"error": "Lesson not found"}), 404

        return jsonify({
            "id": lesson.id,
            "topic": lesson.topic,
            "level": lesson.level,
            "content": lesson.content,
            "created_at": lesson.created_at.strftime("%b %d, %Y at %I:%M %p")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-quiz', methods=['POST'])
@login_required
def generate_quiz():
    content = request.json.get('content')
    if not content or len(content) < 50:
        return jsonify({"error": "Insufficient module data to synthesize quiz."}), 400

    # Rigid JSON Prompt to prevent 422 Errors
    message = (
        "TASK: Generate 5 MCQs based on the text. "
        "FORMAT: Return ONLY a valid JSON object. "
        "SCHEMA: { 'questions': [ { 'question': 'str', 'options': ['str','str','str','str'], 'answer': int_0_3 } ] } "
        f"\n\nTEXT: {content[:1800]}"
    )

    if co is None:
        return jsonify({"error": "AI engine is not configured on the server"}), 500

    try:
        response = co.chat(
            model='command-a-03-2025', 
            message=message, 
            response_format={"type": "json_object"}
        )
        return jsonify(json.loads(response.text))
    except Exception as e:
        print(f"AI FAILURE: {e}")
        return jsonify({"error": "Neural link failed to format quiz data."}), 500

@app.route('/api/save-quiz', methods=['POST'])
@login_required
def save_quiz():
    from datetime import datetime as dt
    data = request.json
    now = dt.now()

    print(f"Saving quiz: Topic='{data.get('topic')}', Score={data.get('score')}/{data.get('total')}")

    # Save quiz result
    new_res = QuizResult(
        topic=data['topic'],
        score=data['score'],
        total=data['total'],
        user_id=current_user.id,
        date_only=now.date(),
        time_only=now.time()
    )
    db.session.add(new_res)

    print(f"QuizResult created for user {current_user.id} on {now.date()}")

    # Automatically update today's study log with quiz results
    stmt = select(StudyLog).filter_by(user_id=current_user.id, date=now.date())
    study_log = db.session.execute(stmt).scalar_one_or_none()

    if not study_log:
        print(f"Creating new StudyLog for {now.date()}")
        study_log = StudyLog(
            user_id=current_user.id,
            date=now.date(),
            study_time_minutes=0,
        )
    else:
        print(f"Updating existing StudyLog for {now.date()}")

    # Add topic to topics covered
    if isinstance(study_log.topics_covered, list):
        if data['topic'] not in study_log.topics_covered:
            study_log.topics_covered.append(data['topic'])
    else:
        study_log.topics_covered = [data['topic']]

    # Update quiz_score with the latest score
    quiz_percentage = (data['score'] / data['total']) * 100
    study_log.quiz_score = quiz_percentage

    print(f"Updated StudyLog: quiz_score={quiz_percentage:.1f}%, topics={study_log.topics_covered}")

    # Add quiz activity
    if isinstance(study_log.learning_activities, list):
        if 'quiz' not in study_log.learning_activities:
            study_log.learning_activities.append('quiz')
    else:
        study_log.learning_activities = ['quiz']

    db.session.add(study_log)
    db.session.commit()

    print(f"Quiz and StudyLog saved successfully")

    return jsonify({
        "status": "success",
        "completed_at": now.strftime('%Y-%m-%d %H:%M:%S'),
        "reset_current_lesson": True  # Signal frontend to clear current lesson
    })

# --- LEARNING PATH GENERATOR ---

@app.route('/api/learner-profile', methods=['GET', 'POST'])
@login_required
def manage_learner_profile():
    if request.method == 'POST':
        data = request.json
        stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
        profile = db.session.execute(stmt).scalar_one_or_none()
        
        if not profile:
            profile = LearnerProfile(user_id=current_user.id)
        
        profile.education_level = data.get('education_level', profile.education_level)
        profile.knowledge_level = data.get('knowledge_level', profile.knowledge_level)
        profile.learning_style = data.get('learning_style', profile.learning_style)
        profile.study_hours_per_week = data.get('study_hours_per_week', profile.study_hours_per_week)
        profile.learning_goal = data.get('learning_goal', profile.learning_goal)
        profile.target_duration_weeks = data.get('target_duration_weeks', profile.target_duration_weeks)
        profile.completed_topics = data.get('completed_topics', profile.completed_topics)
        profile.weak_areas = data.get('weak_areas', profile.weak_areas)
        
        db.session.add(profile)
        db.session.commit()
        return jsonify({"status": "success", "profile_id": profile.id})
    
    else:
        stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
        profile = db.session.execute(stmt).scalar_one_or_none()
        if profile:
            return jsonify({
                "education_level": profile.education_level,
                "knowledge_level": profile.knowledge_level,
                "learning_style": profile.learning_style,
                "study_hours_per_week": profile.study_hours_per_week,
                "learning_goal": profile.learning_goal,
                "target_duration_weeks": profile.target_duration_weeks,
                "completed_topics": profile.completed_topics,
                "weak_areas": profile.weak_areas
            })
        return jsonify({"status": "no_profile"}), 404

@app.route('/api/create-profile', methods=['POST'])
@login_required
def create_or_update_profile():
    """Create or update learner profile"""
    data = request.json

    # Check if profile exists
    stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
    profile = db.session.execute(stmt).scalar_one_or_none()

    if profile:
        # Update existing profile
        profile.learning_goal = data.get('learning_goal', profile.learning_goal)
        profile.study_hours_per_week = data.get('study_hours_per_week', profile.study_hours_per_week)
        profile.education_level = data.get('education_level', profile.education_level)
        profile.target_duration_weeks = data.get('target_duration_weeks', profile.target_duration_weeks)
        profile.learning_style = data.get('learning_style', profile.learning_style)
        profile.knowledge_level = data.get('knowledge_level', profile.knowledge_level)
    else:
        # Create new profile
        profile = LearnerProfile(
            user_id=current_user.id,
            learning_goal=data.get('learning_goal', ''),
            study_hours_per_week=data.get('study_hours_per_week', 5),
            education_level=data.get('education_level', 'undergraduate'),
            target_duration_weeks=data.get('target_duration_weeks', 8),
            learning_style=data.get('learning_style', 'reading'),
            knowledge_level=data.get('knowledge_level', 'intermediate'),
            completed_topics=[],
            weak_areas=[]
        )
        db.session.add(profile)

    db.session.commit()
    return jsonify({"status": "success", "message": "Profile saved successfully"})

@app.route('/api/generate-learning-path', methods=['POST'])
@login_required
def generate_learning_path():
    data = request.json
    
    stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    
    if not profile:
        return jsonify({"error": "Learner profile not found"}), 400
    
    stmt = select(QuizResult).filter_by(user_id=current_user.id).order_by(QuizResult.date.desc()).limit(10)
    recent_results = db.session.execute(stmt).scalars().all()
    
    avg_score = sum([r.score / r.total * 100 for r in recent_results]) / len(recent_results) if recent_results else 50
    
    prompt = f"""
    Create a highly personalized biotechnology learning roadmap in JSON format.
    
    LEARNER PROFILE:
    - Education Level: {profile.education_level}
    - Current Knowledge: {profile.knowledge_level}
    - Learning Style: {profile.learning_style}
    - Study Hours/Week: {profile.study_hours_per_week}
    - Learning Goal: {profile.learning_goal}
    - Target Duration: {profile.target_duration_weeks} weeks
    - Completed Topics: {', '.join(profile.completed_topics) if profile.completed_topics else 'None'}
    - Weak Areas: {', '.join(profile.weak_areas) if profile.weak_areas else 'None'}
    - Recent Quiz Average: {avg_score:.1f}%
    
    TASK: Generate a complete personalized learning path with:
    1. Learning Path (ordered topics from basic to advanced)
    2. Weekly Study Plan (6-week detailed plan)
    3. Progression Strategy (advancement criteria, revision points, mock tests)
    4. Motivation & Tips (personalized advice, focus areas, timeline)
    
    IMPORTANT: Return ONLY valid JSON with this structure:
    {{
        "learning_path": [
            {{"topic": "string", "duration_hours": number, "difficulty": "beginner/intermediate/advanced", "resource_type": "video/notes/simulation/case_study/lab", "description": "string"}}
        ],
        "weekly_plan": [
            {{"week": number, "topics": ["string"], "activities": ["string"], "revision": ["string"], "checkpoint": "string"}}
        ],
        "progression_strategy": {{
            "advancement_criteria": "string",
            "revision_schedule": "string",
            "mock_test_schedule": "string",
            "remedial_topics": ["string"] if applicable
        }},
        "motivation_tips": {{
            "personalized_tips": ["string"],
            "focus_areas": ["string"],
            "predicted_timeline": "string"
        }}
    }}
    """
    
    if co is None:
        return jsonify({"error": "AI engine is not configured on the server"}), 500

    try:
        response = co.chat(
            model='command-a-03-2025',
            message=prompt,
            response_format={"type": "json_object"}
        )
        
        path_data = json.loads(response.text)
        
        stmt = select(LearningPath).filter_by(user_id=current_user.id)
        existing_path = db.session.execute(stmt).scalar_one_or_none()
        
        if existing_path:
            existing_path.path_data = path_data.get('learning_path', [])
            existing_path.weekly_plan = path_data.get('weekly_plan', [])
            existing_path.progression_strategy = path_data.get('progression_strategy', {})
            existing_path.motivation_tips = path_data.get('motivation_tips', {})
            existing_path.profile_id = profile.id
            db.session.commit()
        else:
            learning_path = LearningPath(
                user_id=current_user.id,
                profile_id=profile.id,
                path_data=path_data.get('learning_path', []),
                weekly_plan=path_data.get('weekly_plan', []),
                progression_strategy=path_data.get('progression_strategy', {}),
                motivation_tips=path_data.get('motivation_tips', {})
            )
            db.session.add(learning_path)
            db.session.commit()
        
        return jsonify({
            "status": "success",
            "learning_path": path_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/learning-path')
@login_required
def learning_path_view():
    stmt = select(LearningPath).filter_by(user_id=current_user.id).order_by(LearningPath.created_at.desc())
    learning_path = db.session.execute(stmt).scalar_one_or_none()
    
    stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    
    return render_template('learning_path.html', learning_path=learning_path, profile=profile)

# --- WEEKLY PROGRESS ANALYTICS ---

@app.route('/api/study-log', methods=['POST'])
@login_required
def log_study_session():
    """Log a study session"""
    data = request.json
    from datetime import datetime as dt
    
    study_date = dt.strptime(data.get('date'), '%Y-%m-%d').date()
    now = dt.now()
    
    stmt = select(StudyLog).filter_by(user_id=current_user.id, date=study_date)
    log = db.session.execute(stmt).scalar_one_or_none()
    
    if not log:
        log = StudyLog(user_id=current_user.id, date=study_date)
    
    # Parse start and end times if provided
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    
    if start_time_str:
        log.start_time = dt.strptime(start_time_str, '%H:%M').time()
    if end_time_str:
        log.end_time = dt.strptime(end_time_str, '%H:%M').time()
    
    log.study_time_minutes = data.get('study_time_minutes', 0)
    log.topics_covered = data.get('topics_covered', [])
    log.subtopics = data.get('subtopics', [])
    log.learning_activities = data.get('learning_activities', [])
    log.quiz_score = data.get('quiz_score')
    log.focus_level = data.get('focus_level', 'medium')
    log.feedback = data.get('feedback')
    
    db.session.add(log)
    db.session.commit()
    return jsonify({
        "status": "success",
        "logged_at": now.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/weekly-progress')
@login_required
def get_weekly_progress():
    """Generate weekly progress card with detailed analytics"""
    from datetime import datetime as dt, timedelta
    
    # Get the week starting from Monday of this week
    today = dt.now().date()
    monday = today - timedelta(days=today.weekday())
    
    # Get all study logs for this week
    stmt = select(StudyLog).filter(
        StudyLog.user_id == current_user.id,
        StudyLog.date >= monday,
        StudyLog.date < monday + timedelta(days=7)
    ).order_by(StudyLog.date)
    
    week_logs = db.session.execute(stmt).scalars().all()
    
    # Calculate weekly summary
    total_study_time = sum([log.study_time_minutes for log in week_logs])
    days_with_study = len([log for log in week_logs if log.study_time_minutes > 0])
    avg_daily_study = total_study_time / 7 if total_study_time > 0 else 0

    # Calculate quiz statistics
    quiz_scores = [log.quiz_score for log in week_logs if log.quiz_score is not None]
    avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
    days_with_quiz = len(quiz_scores)

    # Get user's target study time (default 600 min = 10 hours per week)
    stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    target_daily_minutes = (profile.study_hours_per_week * 60 // 7) if profile else 85

    # Calculate consistency score (include quiz engagement)
    consistency_score = 0
    if days_with_study > 0:
        study_consistency = (days_with_study / 7) * 60
        time_consistency = (avg_daily_study / target_daily_minutes) * 30 if target_daily_minutes > 0 else 0
        quiz_consistency = (days_with_quiz / 7) * 10  # Small bonus for quiz engagement
        consistency_score = min(100, study_consistency + time_consistency + quiz_consistency)
    
    # Build daily cards
    daily_cards = []
    all_topics = {}
    
    for i in range(7):
        current_date = monday + timedelta(days=i)
        day_log = next((log for log in week_logs if log.date == current_date), None)
        
        if day_log:
            study_time = day_log.study_time_minutes
            status = "Above Target" if study_time > target_daily_minutes else ("On Track" if study_time >= target_daily_minutes * 0.8 else "Below Target")
            quiz_performance = f"{day_log.quiz_score:.1f}%" if day_log.quiz_score else "No quiz"
            
            # Count topics
            for topic in day_log.topics_covered:
                all_topics[topic] = all_topics.get(topic, 0) + 1
            
            start_time_str = day_log.start_time.strftime('%H:%M:%S') if day_log.start_time else None
            end_time_str = day_log.end_time.strftime('%H:%M:%S') if day_log.end_time else None
            
            daily_cards.append({
                "date": current_date.strftime('%a, %b %d'),
                "day_name": current_date.strftime('%A'),
                "study_time": study_time,
                "status": status,
                "start_time": start_time_str,
                "end_time": end_time_str,
                "topics": day_log.topics_covered,
                "activities": day_log.learning_activities,
                "quiz_score": day_log.quiz_score,
                "focus_level": day_log.focus_level,
                "feedback": day_log.feedback or "Great effort today!"
            })
        else:
            daily_cards.append({
                "date": current_date.strftime('%a, %b %d'),
                "day_name": current_date.strftime('%A'),
                "study_time": 0,
                "status": "Below Target",
                "start_time": None,
                "end_time": None,
                "topics": [],
                "activities": [],
                "quiz_score": None,
                "focus_level": "low",
                "feedback": "No study session logged"
            })
    
    # Find most studied topic
    most_studied_topic = max(all_topics, key=all_topics.get) if all_topics else "None"
    
    # Find best day
    best_day = max([c for c in daily_cards if c['study_time'] > 0], key=lambda x: x['study_time'], default=None)
    
    # Detect trend
    study_times = [c['study_time'] for c in daily_cards]
    first_half = sum(study_times[:3]) / 3 if sum(study_times[:3]) > 0 else 0
    second_half = sum(study_times[4:7]) / 3 if sum(study_times[4:7]) > 0 else 0
    
    if first_half == 0 and second_half == 0:
        trend = "inconsistent"
        trend_color = "yellow"
    elif second_half > first_half * 1.1:
        trend = "increasing"
        trend_color = "green"
    elif second_half < first_half * 0.9:
        trend = "decreasing"
        trend_color = "red"
    else:
        trend = "consistent"
        trend_color = "blue"
    
    # Smart insights
    focus_cards = [c for c in daily_cards if c['focus_level']]
    highest_focus = max(focus_cards, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x['focus_level'], 0))['day_name'] if focus_cards else "None"
    
    insights = {
        "best_performing_day": best_day['day_name'] if best_day else "None",
        "highest_focus_day": highest_focus,
        "improvement_suggestion": "Increase consistency by studying at the same time daily." if consistency_score < 60 else "Great consistency! Consider increasing daily duration.",
        "burnout_warning": "Study time is decreasing. Take a break and recharge!" if trend == "decreasing" and second_half < 30 else None,
        "trend": trend,
        "trend_color": trend_color
    }
    
    return jsonify({
        "week_start": monday.strftime('%Y-%m-%d'),
        "summary": {
            "total_study_time": total_study_time,
            "average_daily_study": round(avg_daily_study, 1),
            "days_with_study": days_with_study,
            "days_with_quiz": days_with_quiz,
            "avg_quiz_score": round(avg_quiz_score, 1),
            "most_studied_topic": most_studied_topic,
            "least_studied_day": [c for c in daily_cards if c['study_time'] == 0][0]['day_name'] if any(c['study_time'] == 0 for c in daily_cards) else "None",
            "consistency_score": round(consistency_score, 1),
            "target_daily_minutes": target_daily_minutes
        },
        "daily_cards": daily_cards,
        "insights": insights,
        "graph_data": {
            "days": [c['day_name'] for c in daily_cards],
            "actual": study_times,
            "target": [target_daily_minutes] * 7
        }
    })

@app.route('/weekly-progress')
@login_required
def weekly_progress_view():
    """Display weekly progress page"""
    return render_template('weekly_progress.html')

@app.route('/profile')
@login_required
def profile_view():
    """Display user profile page with comprehensive information"""
    from datetime import timedelta

    # Get user's learner profile
    stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
    learner_profile = db.session.execute(stmt).scalar_one_or_none()

    # Get quiz statistics
    stmt = select(QuizResult).filter_by(user_id=current_user.id)
    all_quiz_results = db.session.execute(stmt).scalars().all()

    # Calculate quiz stats
    total_quizzes = len(all_quiz_results)
    if total_quizzes > 0:
        avg_score = sum([r.score / r.total * 100 for r in all_quiz_results]) / total_quizzes
        highest_score = max([r.score / r.total * 100 for r in all_quiz_results])
        recent_quizzes = sorted(all_quiz_results, key=lambda x: x.date, reverse=True)[:5]
    else:
        avg_score = 0
        highest_score = 0
        recent_quizzes = []

    # Get study statistics
    stmt = select(StudyLog).filter_by(user_id=current_user.id)
    all_study_logs = db.session.execute(stmt).scalars().all()

    total_study_time = sum([log.study_time_minutes for log in all_study_logs])
    study_days = len([log for log in all_study_logs if log.study_time_minutes > 0])

    # Get learning path info
    stmt = select(LearningPath).filter_by(user_id=current_user.id).order_by(LearningPath.created_at.desc())
    learning_path = db.session.execute(stmt).scalar_one_or_none()

    # Calculate learning streak (consecutive days with study)
    today = datetime.datetime.now().date()
    streak = 0
    for i in range(30):  # Check last 30 days
        check_date = today - timedelta(days=i)
        day_log = next((log for log in all_study_logs if log.date == check_date and log.study_time_minutes > 0), None)
        if day_log:
            streak = i + 1
        else:
            break

    # Get lesson history count
    stmt = select(LessonHistory).filter_by(user_id=current_user.id)
    lesson_count = len(db.session.execute(stmt).scalars().all())

    # Prepare profile data
    profile_data = {
        'user': current_user,
        'learner_profile': learner_profile,
        'stats': {
            'total_quizzes': total_quizzes,
            'avg_quiz_score': round(avg_score, 1),
            'highest_quiz_score': round(highest_score, 1),
            'total_study_hours': round(total_study_time / 60, 1),
            'study_days': study_days,
            'current_streak': streak,
            'generated_lessons': lesson_count,
            'has_learning_path': learning_path is not None
        },
        'recent_quizzes': recent_quizzes
    }

    return render_template('profile.html', **profile_data)

@app.route('/settings')
@login_required
def settings_view():
    """Display user settings page"""
    # Get user's learner profile for settings defaults
    stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
    learner_profile = db.session.execute(stmt).scalar_one_or_none()

    return render_template('settings.html', user=current_user, learner_profile=learner_profile)

@app.route('/help')
@login_required
def help_view():
    """Display help center page"""
    return render_template('help.html')

# --- DASHBOARD API ENDPOINTS ---

@app.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics for current user"""
    from datetime import timedelta

    # Get quiz stats
    stmt = select(QuizResult).filter_by(user_id=current_user.id)
    all_results = db.session.execute(stmt).scalars().all()

    total_quizzes = len(all_results)

    if total_quizzes > 0:
        avg_score = sum([r.score / r.total * 100 for r in all_results]) / total_quizzes
        highest_score = max([r.score / r.total * 100 for r in all_results])
    else:
        avg_score = 0
        highest_score = 0

    # Get study time this week
    today = datetime.datetime.now().date()
    monday = today - timedelta(days=today.weekday())

    stmt = select(StudyLog).filter(
        StudyLog.user_id == current_user.id,
        StudyLog.date >= monday
    )
    week_logs = db.session.execute(stmt).scalars().all()
    weekly_study_time = sum([log.study_time_minutes for log in week_logs])

    # Get streak (consecutive days with study)
    stmt = select(StudyLog).filter_by(user_id=current_user.id).order_by(StudyLog.date.desc())
    all_logs = db.session.execute(stmt).scalars().all()

    streak = 0
    if all_logs:
        current_date = today
        for log in all_logs:
            if log.date == current_date and log.study_time_minutes > 0:
                streak += 1
                current_date = current_date - timedelta(days=1)
            elif log.date < current_date:
                break

    # Get recent topics
    recent_topics = []
    if all_results:
        recent_results = sorted(all_results, key=lambda x: x.date, reverse=True)[:5]
        recent_topics = [{"topic": r.topic, "score": r.score, "total": r.total, "date": r.date.strftime('%b %d')} for r in recent_results]

    return jsonify({
        "total_quizzes": total_quizzes,
        "avg_score": round(avg_score, 1),
        "highest_score": round(highest_score, 1),
        "weekly_study_minutes": weekly_study_time,
        "current_streak": streak,
        "recent_topics": recent_topics
    })

# --- SETTINGS API ENDPOINTS ---

@app.route('/api/user-settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """Get or update user account settings"""
    if request.method == 'GET':
        # Get user's learner profile for settings display
        stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
        learner_profile = db.session.execute(stmt).scalar_one_or_none()

        return jsonify({
            "username": current_user.username,
            "email": current_user.email or "",
            "profile_picture": current_user.profile_picture or "",
            "learning_preferences": {
                "education_level": learner_profile.education_level if learner_profile else "undergraduate",
                "knowledge_level": learner_profile.knowledge_level if learner_profile else "beginner",
                "learning_style": learner_profile.learning_style if learner_profile else "mixed",
                "study_hours_per_week": learner_profile.study_hours_per_week if learner_profile else 10
            }
        })

    elif request.method == 'POST':
        data = request.json

        # Update user basic info
        if 'username' in data:
            # Check if username is already taken
            stmt = select(User).filter(User.username == data['username'], User.id != current_user.id)
            existing_user = db.session.execute(stmt).scalar_one_or_none()
            if existing_user:
                return jsonify({"error": "Username already taken"}), 400
            current_user.username = data['username']

        if 'email' in data:
            current_user.email = data['email']

        # Update learning preferences
        stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
        learner_profile = db.session.execute(stmt).scalar_one_or_none()

        if not learner_profile:
            learner_profile = LearnerProfile(user_id=current_user.id)
            db.session.add(learner_profile)

        if 'learning_preferences' in data:
            prefs = data['learning_preferences']
            learner_profile.education_level = prefs.get('education_level', learner_profile.education_level)
            learner_profile.knowledge_level = prefs.get('knowledge_level', learner_profile.knowledge_level)
            learner_profile.learning_style = prefs.get('learning_style', learner_profile.learning_style)
            learner_profile.study_hours_per_week = prefs.get('study_hours_per_week', learner_profile.study_hours_per_week)

        db.session.commit()
        return jsonify({"status": "success", "message": "Settings updated successfully"})

@app.route('/api/update-password', methods=['POST'])
@login_required
def update_password():
    """Update user password"""
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"error": "Both current and new passwords are required"}), 400

    # Check if user has a password (for OAuth users)
    if not current_user.password:
        return jsonify({"error": "Password cannot be changed for social login accounts"}), 400

    # Verify current password
    if not check_password_hash(current_user.password, current_password):
        return jsonify({"error": "Current password is incorrect"}), 400

    # Update password
    current_user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"status": "success", "message": "Password updated successfully"})

@app.route('/api/privacy-settings', methods=['POST'])
@login_required
def privacy_settings():
    """Update privacy settings (stored in session/localStorage)"""
    data = request.json

    # For now, we'll return success as privacy settings are handled client-side
    # In a production app, you'd store these in a UserSettings table
    return jsonify({"status": "success", "message": "Privacy settings updated"})

@app.route('/api/notification-settings', methods=['POST'])
@login_required
def notification_settings():
    """Update notification preferences"""
    data = request.json

    # For now, we'll return success as notification settings are handled client-side
    # In a production app, you'd store these in a UserSettings table
    return jsonify({"status": "success", "message": "Notification settings updated"})

@app.route('/api/export-data', methods=['GET'])
@login_required
def export_user_data():
    """Export user's learning data"""
    try:
        # Get all user data
        stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
        learner_profile = db.session.execute(stmt).scalar_one_or_none()

        stmt = select(QuizResult).filter_by(user_id=current_user.id)
        quiz_results = db.session.execute(stmt).scalars().all()

        stmt = select(StudyLog).filter_by(user_id=current_user.id)
        study_logs = db.session.execute(stmt).scalars().all()

        stmt = select(LessonHistory).filter_by(user_id=current_user.id)
        lesson_history = db.session.execute(stmt).scalars().all()

        stmt = select(LearningPath).filter_by(user_id=current_user.id)
        learning_paths = db.session.execute(stmt).scalars().all()

        # Compile data
        export_data = {
            "user_info": {
                "username": current_user.username,
                "email": current_user.email,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "export_date": datetime.datetime.now().isoformat()
            },
            "learner_profile": {
                "education_level": learner_profile.education_level if learner_profile else None,
                "knowledge_level": learner_profile.knowledge_level if learner_profile else None,
                "learning_style": learner_profile.learning_style if learner_profile else None,
                "study_hours_per_week": learner_profile.study_hours_per_week if learner_profile else None,
                "learning_goal": learner_profile.learning_goal if learner_profile else None,
                "completed_topics": learner_profile.completed_topics if learner_profile else [],
                "weak_areas": learner_profile.weak_areas if learner_profile else []
            },
            "quiz_results": [
                {
                    "topic": result.topic,
                    "score": result.score,
                    "total": result.total,
                    "date": result.date.isoformat() if result.date else None
                } for result in quiz_results
            ],
            "study_logs": [
                {
                    "date": log.date.isoformat() if log.date else None,
                    "study_time_minutes": log.study_time_minutes,
                    "topics_covered": log.topics_covered,
                    "learning_activities": log.learning_activities,
                    "quiz_score": log.quiz_score,
                    "focus_level": log.focus_level
                } for log in study_logs
            ],
            "lesson_history": [
                {
                    "topic": lesson.topic,
                    "level": lesson.level,
                    "created_at": lesson.created_at.isoformat() if lesson.created_at else None
                } for lesson in lesson_history
            ],
            "learning_paths": [
                {
                    "created_at": path.created_at.isoformat() if path.created_at else None,
                    "path_data": path.path_data,
                    "weekly_plan": path.weekly_plan
                } for path in learning_paths
            ]
        }

        return jsonify({
            "status": "success",
            "data": export_data,
            "filename": f"biolearn_data_{current_user.username}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account and all associated data"""
    data = request.json
    password = data.get('password')

    # Verify password for account deletion
    if current_user.password and not check_password_hash(current_user.password, password):
        return jsonify({"error": "Password verification failed"}), 400

    try:
        user_id = current_user.id

        # Delete all associated data
        db.session.query(LearnerProfile).filter_by(user_id=user_id).delete()
        db.session.query(QuizResult).filter_by(user_id=user_id).delete()
        db.session.query(StudyLog).filter_by(user_id=user_id).delete()
        db.session.query(LessonHistory).filter_by(user_id=user_id).delete()
        db.session.query(LearningPath).filter_by(user_id=user_id).delete()

        # Delete user account
        db.session.delete(current_user)
        db.session.commit()

        # Logout user
        logout_user()
        session.clear()

        return jsonify({"status": "success", "message": "Account deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user's personal information"""
    try:
        data = request.json

        # Update user personal information
        if 'firstName' in data:
            current_user.first_name = data['firstName'].strip() if data['firstName'] else None

        if 'lastName' in data:
            current_user.last_name = data['lastName'].strip() if data['lastName'] else None

        if 'username' in data:
            username = data['username'].strip()
            if username != current_user.username:
                # Check if username is already taken
                stmt = select(User).filter(User.username == username, User.id != current_user.id)
                existing_user = db.session.execute(stmt).scalar_one_or_none()
                if existing_user:
                    return jsonify({"error": "Username already taken"}), 400
                current_user.username = username

        if 'email' in data:
            email = data['email'].strip() if data['email'] else None
            if email != current_user.email:
                # Check if email is already taken
                if email:
                    stmt = select(User).filter(User.email == email, User.id != current_user.id)
                    existing_user = db.session.execute(stmt).scalar_one_or_none()
                    if existing_user:
                        return jsonify({"error": "Email already taken"}), 400
                current_user.email = email

        if 'age' in data:
            try:
                age = int(data['age']) if data['age'] else None
                if age is not None and (age < 13 or age > 100):
                    return jsonify({"error": "Age must be between 13 and 100"}), 400
                current_user.age = age
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid age format"}), 400

        if 'gender' in data:
            current_user.gender = data['gender'] if data['gender'] else None

        if 'phone' in data:
            current_user.phone = data['phone'].strip() if data['phone'] else None

        if 'location' in data:
            current_user.location = data['location'].strip() if data['location'] else None

        if 'qualification' in data:
            current_user.qualification = data['qualification'] if data['qualification'] else None

        if 'university' in data:
            current_user.university = data['university'].strip() if data['university'] else None

        if 'occupation' in data:
            current_user.occupation = data['occupation'].strip() if data['occupation'] else None

        if 'bio' in data:
            current_user.bio = data['bio'].strip() if data['bio'] else None

        # Update the updated_at timestamp
        current_user.updated_at = datetime.datetime.utcnow()

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Profile updated successfully"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-profile', methods=['GET'])
@login_required
def get_profile():
    """Get user's complete profile information"""
    try:
        # Get learner profile
        stmt = select(LearnerProfile).filter_by(user_id=current_user.id)
        learner_profile = db.session.execute(stmt).scalar_one_or_none()

        profile_data = {
            "personal_info": {
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "username": current_user.username,
                "email": current_user.email,
                "age": current_user.age,
                "gender": current_user.gender,
                "phone": current_user.phone,
                "location": current_user.location,
                "qualification": current_user.qualification,
                "university": current_user.university,
                "occupation": current_user.occupation,
                "bio": current_user.bio,
                "profile_picture": current_user.profile_picture,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
            },
            "learning_profile": {
                "education_level": learner_profile.education_level if learner_profile else None,
                "knowledge_level": learner_profile.knowledge_level if learner_profile else None,
                "learning_style": learner_profile.learning_style if learner_profile else None,
                "study_hours_per_week": learner_profile.study_hours_per_week if learner_profile else None,
                "learning_goal": learner_profile.learning_goal if learner_profile else None,
                "target_duration_weeks": learner_profile.target_duration_weeks if learner_profile else None
            }
        }

        return jsonify(profile_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- SYSTEM INITIALIZATION ---

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except:
            pass
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true')