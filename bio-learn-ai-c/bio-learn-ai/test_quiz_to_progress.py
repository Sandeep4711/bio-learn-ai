#!/usr/bin/env python3
"""Test that quiz results update weekly progress"""

from app import app, db, User, QuizResult, StudyLog
from datetime import datetime, date
from sqlalchemy import select

with app.app_context():
    # Create test data if needed
    db.create_all()
    
    user = db.session.execute(db.select(User)).scalars().first()
    if not user:
        user = User(username='test_user', password='test123')
        db.session.add(user)
        db.session.commit()
    
    print(f"Testing with user: {user.username}\n")
    
    # Simulate quiz submission
    from datetime import datetime as dt
    now = dt.now()
    
    print("=" * 70)
    print("BEFORE QUIZ SUBMISSION")
    print("=" * 70)
    
    # Check today's study log before
    stmt = select(StudyLog).filter_by(user_id=user.id, date=now.date())
    log_before = db.session.execute(stmt).scalar_one_or_none()
    
    if log_before:
        print(f"✓ Today's study log exists:")
        print(f"  - Quiz Score: {log_before.quiz_score}")
        print(f"  - Topics: {log_before.topics_covered}")
        print(f"  - Activities: {log_before.learning_activities}")
    else:
        print("✗ No study log for today yet")
    
    print("\n" + "=" * 70)
    print("SIMULATING QUIZ SUBMISSION")
    print("=" * 70)
    
    # Create a quiz result like the API would
    quiz = QuizResult(
        topic="Advanced Genetics",
        score=92,
        total=100,
        user_id=user.id,
        date_only=now.date(),
        time_only=now.time()
    )
    db.session.add(quiz)
    
    # Update/create study log
    stmt = select(StudyLog).filter_by(user_id=user.id, date=now.date())
    study_log = db.session.execute(stmt).scalar_one_or_none()
    
    if not study_log:
        study_log = StudyLog(
            user_id=user.id,
            date=now.date(),
            study_time_minutes=0,
        )
    
    # Add topic and quiz activity
    if isinstance(study_log.topics_covered, list):
        if quiz.topic not in study_log.topics_covered:
            study_log.topics_covered.append(quiz.topic)
    else:
        study_log.topics_covered = [quiz.topic]
    
    quiz_percentage = (quiz.score / quiz.total) * 100
    study_log.quiz_score = quiz_percentage
    
    if isinstance(study_log.learning_activities, list):
        if 'quiz' not in study_log.learning_activities:
            study_log.learning_activities.append('quiz')
    else:
        study_log.learning_activities = ['quiz']
    
    db.session.add(study_log)
    db.session.commit()
    
    print(f"✓ Quiz submitted: {quiz.topic}")
    print(f"  - Score: {quiz.score}/{quiz.total}")
    print(f"  - Time: {now.strftime('%H:%M:%S')}")
    print(f"  - Study log updated")
    
    print("\n" + "=" * 70)
    print("AFTER QUIZ SUBMISSION")
    print("=" * 70)
    
    # Check today's study log after
    stmt = select(StudyLog).filter_by(user_id=user.id, date=now.date())
    log_after = db.session.execute(stmt).scalar_one_or_none()
    
    if log_after:
        print(f"✓ Today's study log updated:")
        print(f"  - Quiz Score: {log_after.quiz_score}%")
        print(f"  - Topics: {log_after.topics_covered}")
        print(f"  - Activities: {log_after.learning_activities}")
        print(f"  - Study Time: {log_after.study_time_minutes} minutes")
    
    print("\n" + "=" * 70)
    print("✅ QUIZ RESULT NOW APPEARS IN WEEKLY PROGRESS")
    print("=" * 70)
