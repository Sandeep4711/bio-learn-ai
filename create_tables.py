from app import app, db
from sqlalchemy.exc import OperationalError

import os


def mask_database_url(url: str | None) -> str:
    if not url:
        return "<missing DATABASE_URL>"
    if '@' not in url:
        return url
    left, right = url.split('@', 1)
    if ':' in left:
        prefix, _password = left.rsplit(':', 1)
        return f"{prefix}:***@{right}"
    return f"***@{right}"


print("DB URL:", mask_database_url(os.getenv("DATABASE_URL")))

with app.app_context():
    try:
        db.create_all()
        print("Tables created successfully")
    except OperationalError as e:
        print("Database connection failed.")
        print("Verify DATABASE_URL username/password/host/port and Supabase pooler settings.")
        raise