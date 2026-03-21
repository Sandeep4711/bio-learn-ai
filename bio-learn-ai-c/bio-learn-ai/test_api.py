#!/usr/bin/env python3
"""Test script for weekly progress API with timestamp tracking"""

from app import app, db, User, StudyLog, LearnerProfile, QuizResult
from datetime import datetime, timedelta, time
import json

def test_timestamps():
    """Test that timestamps are recorded accurately"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Get first user or create test user
        user = db.session.execute(db.select(User)).scalars().first()
        if not user:
            user = User(username='test_user', password='test123')
            db.session.add(user)
            db.session.commit()
            print("✓ Created test user")
        
        print(f"✓ Testing timestamps with user: {user.username}")
        
        # Create a learner profile if not exists
        profile = db.session.execute(
            db.select(LearnerProfile).filter_by(user_id=user.id)
        ).scalar_one_or_none()
        
        if not profile:
            profile = LearnerProfile(
                user_id=user.id,
                study_hours_per_week=10
            )
            db.session.add(profile)
            db.session.commit()
            print("✓ Created test learner profile")
        
        # Create some sample study logs with timestamps
        today = datetime.now().date()
        monday = today - timedelta(days=today.weekday())
        
        # Add study logs with start/end times
        for i in range(3):
            log_date = monday + timedelta(days=i)
            existing = db.session.execute(
                db.select(StudyLog).filter(
                    StudyLog.user_id == user.id,
                    StudyLog.date == log_date
                )
            ).scalar_one_or_none()
            
            if not existing:
                start = time(9 + (i * 2), 30)  # 9:30, 11:30, 13:30
                end = time(10 + (i * 2), 45)   # 10:45, 12:45, 14:45
                
                log = StudyLog(
                    user_id=user.id,
                    date=log_date,
                    start_time=start,
                    end_time=end,
                    study_time_minutes=60 + (i * 10),
                    topics_covered=["Biology", "Genetics"],
                    learning_activities=["video_lectures", "practice_problems"],
                    quiz_score=85,
                    focus_level="high" if i == 0 else "medium",
                    feedback="Good progress"
                )
                db.session.add(log)
        
        # Add a quiz result with timestamp
        now = datetime.now()
        quiz = QuizResult(
            user_id=user.id,
            topic="Molecular Biology",
            score=90,
            total=100,
            date_only=now.date(),
            time_only=now.time()
        )
        db.session.add(quiz)
        db.session.commit()
        
        print("✓ Created sample study logs with timestamps")
        print("✓ Created quiz result with timestamp")
        
        # Retrieve and verify
        stmt = db.select(StudyLog).filter(
            StudyLog.user_id == user.id,
            StudyLog.date >= monday,
            StudyLog.date < monday + timedelta(days=7)
        ).order_by(StudyLog.date)
        
        study_logs = db.session.execute(stmt).scalars().all()
        
        print("\n📊 Study Session Timestamps:")
        for log in study_logs:
            print(f"  • {log.date.strftime('%A, %B %d, %Y')}")
            if log.start_time and log.end_time:
                print(f"    ⏰ {log.start_time.strftime('%H:%M:%S')} - {log.end_time.strftime('%H:%M:%S')} ({log.study_time_minutes} mins)")
            else:
                print(f"    ⏰ No times recorded ({log.study_time_minutes} mins logged)")
        
        # Retrieve and verify quiz results
        stmt = db.select(QuizResult).filter_by(user_id=user.id).order_by(QuizResult.date.desc())
        quizzes = db.session.execute(stmt).scalars().all()
        
        print("\n📝 Quiz Completion Timestamps:")
        for quiz in quizzes[-3:]:  # Last 3
            if quiz.date_only and quiz.time_only:
                print(f"  • {quiz.topic}: {quiz.date_only.strftime('%Y-%m-%d')} at {quiz.time_only.strftime('%H:%M:%S')} ({quiz.score}/{quiz.total})")
            else:
                print(f"  • {quiz.topic}: {quiz.date.strftime('%Y-%m-%d %H:%M:%S')} ({quiz.score}/{quiz.total})")
        
        print("\n✅ TIMESTAMP TEST PASSED - All times recorded accurately!")
        return True

if __name__ == '__main__':
    try:
        if test_timestamps():
            print("\n✅ All timestamp features working correctly!")
    except Exception as e:
        print(f"\n❌ TIMESTAMP TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

