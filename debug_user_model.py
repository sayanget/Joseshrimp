import os
from app import create_app, db
from app.models import User
from sqlalchemy import text

def debug_user():
    print("Debug User Model...")
    app = create_app('production')
    with app.app_context():
        # Check model columns
        print("Model columns:")
        for col in User.__table__.columns:
            print(f"  - {col.name}: {col.type}")
            
        # Check actual DB columns
        db_url = os.environ.get('DATABASE_URL')
        if db_url and db_url.startswith("postgres://"):
            os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)
            
        print("\nChecking DB columns via SQL:")
        try:
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'user'"))
            for row in result:
                print(f"  - {row[0]}")
        except Exception as e:
            print(f"Error querying schema: {e}")

        # Force Drop and Create using Table object
        print("\nForcing Drop and Create...")
        try:
            User.__table__.drop(db.engine, checkfirst=True)
            print("Table dropped.")
            User.__table__.create(db.engine)
            print("Table created.")
        except Exception as e:
            print(f"Error during drop/create: {e}")

if __name__ == "__main__":
    debug_user()
