import os
from app import create_app, db
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from datetime import datetime

def raw_seed_admin():
    print("Raw Seeding Admin...")
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        # 1. Get Role ID
        try:
            result = db.session.execute(text("SELECT id FROM role WHERE name = 'Administrator'"))
            role_row = result.fetchone()
            if not role_row:
                print("Role 'Administrator' not found. Creating...")
                # Create role manually or fail? Let's fail for now or Insert.
                db.session.execute(text("INSERT INTO role (name, description) VALUES ('Administrator', 'System Admin')"))
                db.session.commit()
                result = db.session.execute(text("SELECT id FROM role WHERE name = 'Administrator'"))
                role_row = result.fetchone()
            
            role_id = role_row[0]
            print(f"Role ID: {role_id}")
            
            # 2. Check if user exists
            result = db.session.execute(text("SELECT id FROM \"user\" WHERE username = 'admin'"))
            if result.fetchone():
                print("User 'admin' already exists.")
                return

            # 3. Insert User
            print("Inserting user...")
            password_hash = generate_password_hash('admin123')
            now = datetime.utcnow()
            
            # Try inserting WITH last_login
            try:
                sql = text("""
                    INSERT INTO "user" (username, password_hash, active, role_id, created_at, last_login)
                    VALUES (:u, :p, :a, :r, :c, :l)
                """)
                db.session.execute(sql, {'u': 'admin', 'p': password_hash, 'a': True, 'r': role_id, 'c': now, 'l': None})
                db.session.commit()
                print("User 'admin' created successfully (with last_login).")
                return
            except Exception as e:
                print(f"Failed with last_login: {e}")
                db.session.rollback()
                
            # Try inserting WITHOUT last_login
            print("Retrying without last_login...")
            sql = text("""
                INSERT INTO "user" (username, password_hash, active, role_id, created_at)
                VALUES (:u, :p, :a, :r, :c)
            """)
            db.session.execute(sql, {'u': 'admin', 'p': password_hash, 'a': True, 'r': role_id, 'c': now})
            db.session.commit()
            print("User 'admin' created successfully (WITHOUT last_login).")

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    raw_seed_admin()
