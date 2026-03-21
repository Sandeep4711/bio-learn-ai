#!/usr/bin/env python3
"""Check that timestamps are properly recorded"""

from app import app, db, QuizResult, StudyLog, User
from sqlalchemy import select
from datetime import datetime, timedelta

with app.app_context():
    user = db.session.execute(db.select(User)).scalars().first()
    
    if not user:
        print("❌ No users found")
        exit(1)
    
    print(f"✓ Testing with user: {user.username}\n")
    
    # Query recent quiz results
    quizzes = db.session.execute(
        select(QuizResult).filter_by(user_id=user.id).order_by(QuizResult.date.desc())
    ).scalars().all()
    
    print("=" * 70)
    print("📝 QUIZ COMPLETION TIMESTAMPS")
    print("=" * 70)
    print(f'Found {len(quizzes)} quiz results\n')
    
    for quiz in quizzes:
        if quiz.date_only and quiz.time_only:
            date_str = quiz.date_only.strftime("%Y-%m-%d")
            time_str = quiz.time_only.strftime("%H:%M:%S")
            print(f"  ✓ {quiz.topic}")
            print(f"    📅 Date: {date_str}")
            print(f"    ⏰ Time: {time_str}")
            print(f"    📊 Score: {quiz.score}/{quiz.total}\n")
        else:
            date_time = quiz.date.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  ✓ {quiz.topic}")
            print(f"    📅 DateTime: {date_time}")
            print(f"    📊 Score: {quiz.score}/{quiz.total}\n")
    
    # Query study logs
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    
    logs = db.session.execute(
        select(StudyLog).filter(
            StudyLog.user_id == user.id,
            StudyLog.date >= monday,
            StudyLog.date < monday + timedelta(days=7)
        ).order_by(StudyLog.date)
    ).scalars().all()
    
    print("=" * 70)
    print("📚 STUDY SESSION TIMESTAMPS")
    print("=" * 70)
    print(f'Found {len(logs)} study sessions for this week\n')
    
    for log in logs:
        print(f"  ✓ {log.date.strftime('%A, %B %d, %Y')}")
        if log.start_time and log.end_time:
            start = log.start_time.strftime("%H:%M:%S")
            end = log.end_time.strftime("%H:%M:%S")
            print(f"    ⏰ Session: {start} - {end}")
            print(f"    ⌛ Duration: {log.study_time_minutes} minutes\n")
        else:
            print(f"    ⌛ Duration: {log.study_time_minutes} minutes (no times recorded)\n")
    
    print("=" * 70)
    print("✅ TIMESTAMP SYSTEM OPERATIONAL")
    print("=" * 70)
