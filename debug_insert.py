import os
from app import create_app, db
from sqlalchemy import text
from datetime import datetime

def debug_insert():
    print("Debug Inserting Single User...")
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        try:
            # 1. Create a dummy role if needed (assuming roles exist from previous run or we create one)
            # Actually, let's just insert with role_id=1 (Admin usually)
            
            # 2. Insert User
            sql = text("""
                INSERT INTO "user" (id, username, password_hash, active, role_id, created_at, last_login)
                VALUES (:id, :u, :p, :a, :r, :c, :l)
            """)
            
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
            
            params = {
                'id': 9999,
                'u': 'debug_user',
                'p': 'debug_pass',
                'a': True,
                'r': 1, # Assuming role 1 exists
                'c': current_time,
                'l': current_time
            }
            
            print(f"Params: {params}")
            db.session.execute(sql, params)
            db.session.commit()
            print("Debug Insert Successful!")
            
            # Clean up
            db.session.execute(text("DELETE FROM \"user\" WHERE id = 9999"))
            db.session.commit()
            
        except Exception as e:
            print(f"Debug Insert Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_insert()
