import os
from app import create_app, db
from app.models import User
from sqlalchemy import text

def fix_user_table():
    print("Fixing User table...")
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        # Drop user table
        print("Dropping 'user' table...")
        try:
            db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
            db.session.commit()
            print("Dropped.")
        except Exception as e:
            print(f"Error dropping table: {e}")
            db.session.rollback()

        # Recreate tables
        print("Recreating tables...")
        db.create_all() # This will create 'user' table with new schema
        print("Done.")

if __name__ == "__main__":
    fix_user_table()
