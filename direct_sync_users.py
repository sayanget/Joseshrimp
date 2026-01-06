import sqlite3
import os
from app import create_app, db
from sqlalchemy import text
from datetime import datetime

def direct_sync():
    print("Direct Syncing users from local sales.db to production [Raw SQL]...")
    
    # 1. Read Local Data
    print("Reading local data...")
    local_conn = sqlite3.connect('instance/sales.db')
    local_conn.row_factory = sqlite3.Row
    cur = local_conn.cursor()
    
    cur.execute("SELECT * FROM permission")
    local_permissions = [dict(row) for row in cur.fetchall()]
    
    cur.execute("SELECT * FROM role")
    local_roles = [dict(row) for row in cur.fetchall()]
    
    cur.execute("SELECT * FROM user")
    local_users = [dict(row) for row in cur.fetchall()]
    
    local_roles_permissions = []
    try:
        cur.execute("SELECT * FROM roles_permissions")
        local_roles_permissions = [dict(row) for row in cur.fetchall()]
    except:
        pass
        
    local_conn.close()
    print(f"Read: {len(local_users)} users.")

    # 2. Connect to Production
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        # 3. Truncate
        print("Truncating tables...", flush=True)
        try:
            db.session.execute(text('TRUNCATE TABLE roles_permissions, "user", role, permission CASCADE'))
            db.session.commit()
            print("Truncated.", flush=True)
        except Exception as e:
            print(f"Truncate failed, trying DELETE: {e}", flush=True)
            db.session.rollback()
            try:
                db.session.execute(text('DELETE FROM roles_permissions'))
                db.session.execute(text('DELETE FROM "user"'))
                db.session.execute(text('DELETE FROM role'))
                db.session.execute(text('DELETE FROM permission'))
                db.session.commit()
            except Exception as e2:
                print(f"DELETE failed: {e2}", flush=True)
                return

        # 4. Insert Permissions
        print("Inserting Permissions...", flush=True)
        for p in local_permissions:
            sql = text("INSERT INTO permission (id, name, description) VALUES (:id, :name, :desc)")
            db.session.execute(sql, {'id': p['id'], 'name': p['name'], 'desc': p.get('description')})
            
        # 5. Insert Roles
        print("Inserting Roles...", flush=True)
        for r in local_roles:
            sql = text("INSERT INTO role (id, name, description) VALUES (:id, :name, :desc)")
            db.session.execute(sql, {'id': r['id'], 'name': r['name'], 'desc': r.get('description')})
            
        # 6. Insert Roles Permissions
        print("Inserting Roles-Permissions...", flush=True)
        for rp in local_roles_permissions:
            sql = text("INSERT INTO roles_permissions (role_id, permission_id) VALUES (:rid, :pid)")
            db.session.execute(sql, {'rid': rp['role_id'], 'pid': rp['permission_id']})

        # 7. Insert Users
        print("Inserting Users...", flush=True)
        for u in local_users:
            # Handle potential missing Created At / Last Login in local DB
            created_at = u.get('created_at')
            if not created_at:
                created_at = datetime.utcnow()
                
            # Check if last_login is in local dict
            last_login = u.get('last_login')
            
            # Construct SQL dynamically based on availability
            # But "user" schema in Prod definitely has last_login now (based on previous steps)
            
            sql = text("""
                INSERT INTO "user" (id, username, password_hash, active, role_id, created_at, last_login)
                VALUES (:id, :u, :p, :a, :r, :c, :l)
            """)
            
            params = {
                'id': u['id'],
                'u': u['username'],
                'p': u['password_hash'],
                'a': bool(u['active']),
                'r': u['role_id'],
                'c': created_at,
                'l': last_login
            }
            
            db.session.execute(sql, params)

        try:
            db.session.commit()
            print("Sync Successful!", flush=True)
            
            # Reset Sequences
            for table in ['user', 'role', 'permission']:
                try:
                    db.session.execute(text(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM \"{table}\"))"))
                except:
                    pass
            db.session.commit()
            
        except Exception as e:
            print(f"Commit failed: {e}", flush=True)
            db.session.rollback()

if __name__ == "__main__":
    direct_sync()
