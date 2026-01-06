import sqlite3
import os
from app import create_app, db
from app.models import User, Role, Permission
from sqlalchemy import text
from datetime import datetime

def rebuild_and_sync():
    print("Rebuilding and Syncing Auth Tables...")
    
    # 1. Read Local Data
    print("Reading local data...")
    local_data = {}
    
    conn = sqlite3.connect('instance/sales.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    for table in ['permission', 'role', 'user', 'roles_permissions']:
        try:
            cur.execute(f"SELECT * FROM {table}")
            local_data[table] = [dict(row) for row in cur.fetchall()]
            print(f"  - {table}: {len(local_data[table])} records")
        except sqlite3.Error as e:
            print(f"  - {table}: Error reading ({e})")
            local_data[table] = []
            
    conn.close()

    if not local_data['user']:
        print("No users found locally. Aborting to prevent data loss.")
        return

    # 2. Connect to Production
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        # 3. Drop existing tables
        print("Dropping existing tables...", flush=True)
        try:
            # Order matters: roles_permissions -> user -> role -> permission
            db.session.execute(text('DROP TABLE IF EXISTS roles_permissions CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS role CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS permission CASCADE'))
            db.session.commit()
            print("Tables dropped.", flush=True)
        except Exception as e:
            print(f"Error dropping tables: {e}")
            db.session.rollback()
            return

        # 4. Recreate tables
        print("Recreating tables schema...", flush=True)
        try:
            # We use db.create_all() but usually that creates ALL tables. 
            # Since other tables (sale, customer etc) exist, it should skip them and only create missing ones.
            db.create_all()
            print("Tables recreated.", flush=True)
        except Exception as e:
            print(f"Error creating tables: {e}")
            return

        # 5. Insert Data
        print("Inserting data...", flush=True)
        try:
            # Permissions
            for r in local_data['permission']:
                db.session.execute(
                    text("INSERT INTO permission (id, name, description) VALUES (:id, :name, :d)"),
                    {'id': r['id'], 'name': r['name'], 'd': r['description']}
                )
            
            # Roles
            for r in local_data['role']:
                db.session.execute(
                    text("INSERT INTO role (id, name, description) VALUES (:id, :name, :d)"),
                    {'id': r['id'], 'name': r['name'], 'd': r['description']}
                )
                
            # Roles Permissions
            for r in local_data['roles_permissions']:
                db.session.execute(
                    text("INSERT INTO roles_permissions (role_id, permission_id) VALUES (:rid, :pid)"),
                    {'rid': r['role_id'], 'pid': r['permission_id']}
                )

            # Users
            from dateutil import parser
            
            for u in local_data['user']:
                # Handle boolean conversion from sqlite (1/0) if necessary, strictly checking
                active = bool(u['active'])
                
                # Handle timestamps. Local might be string or None.
                created_at = u.get('created_at')
                created_at_val = None
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            # If it's already a string, it might be fine, but let's normalize
                            dt = parser.parse(created_at)
                            created_at_val = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                        except:
                            created_at_val = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                    else:
                         created_at_val = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                else:
                    created_at_val = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
                
                last_login = u.get('last_login')
                last_login_val = None
                if last_login and isinstance(last_login, str):
                    try:
                        dt = parser.parse(last_login)
                        last_login_val = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                    except:
                        last_login_val = None
                
                sql = text("""
                    INSERT INTO "user" (id, username, password_hash, active, role_id, created_at, last_login)
                    VALUES (:id, :u, :p, :a, :r, :c, :l)
                """)
                db.session.execute(sql, {
                    'id': u['id'],
                    'u': u['username'],
                    'p': u['password_hash'],
                    'a': active,
                    'r': u['role_id'],
                    'c': created_at_val,
                    'l': last_login_val
                })
                
            db.session.commit()
            print("Data inserted.", flush=True)
            
            # 6. Reset Sequences
            print("Resetting sequences...", flush=True)
            for table in ['user', 'role', 'permission']:
                try:
                    db.session.execute(text(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM \"{table}\"))"))
                except Exception as seq_e:
                    print(f"Sequence reset warning for {table}: {seq_e}")
            db.session.commit()
            print("Sync Complete!", flush=True)

        except Exception as e:
            print(f"Error during insertion: {e}")
            db.session.rollback()

if __name__ == "__main__":
    rebuild_and_sync()
