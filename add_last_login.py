import os
from app import create_app, db
from sqlalchemy import text

def add_column():
    print("Adding last_login column...")
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        try:
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS last_login TIMESTAMP'))
            db.session.commit()
            print("Column added (or already existed).")
        except Exception as e:
            print(f"Error adding column: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_column()
