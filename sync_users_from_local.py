import sqlite3
import os
from app import create_app, db
from app.models import User, Role, Permission
from sqlalchemy import text

def sync_users():
    print("Syncing users from local sales.db to production...")
    
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
    
    # Check for roles_permissions table
    local_roles_permissions = []
    try:
        cur.execute("SELECT * FROM roles_permissions")
        local_roles_permissions = [dict(row) for row in cur.fetchall()]
    except sqlite3.Error:
        print("Local roles_permissions table not found or empty.")
        
    local_conn.close()
    
    print(f"Read: {len(local_permissions)} permissions, {len(local_roles)} roles, {len(local_users)} users.")

    # 2. Connect to Production DB
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        # 3. Clear existing auth data
        print("Clearing production auth tables...", flush=True)
        
        def safe_delete(table_name):
            try:
                db.session.execute(text(f'DELETE FROM {table_name}'))
                db.session.commit()
                print(f"Deleted {table_name}.", flush=True)
            except Exception as e:
                db.session.rollback()
                print(f"Failed to delete {table_name} (might not exist): {e}", flush=True)

        safe_delete('roles_permissions')
        safe_delete('"user"')
        safe_delete('role')
        safe_delete('permission')
        print("Clear phase done.", flush=True)

        # 4. Insert Data
        print("Inserting data...")
        
        try:
            # Permissions
            perm_map = {} 
            for p_data in local_permissions:
                p = Permission(id=p_data['id'], name=p_data['name'], description=p_data.get('description'))
                db.session.add(p)
                perm_map[p_data['id']] = p
            
            # Roles
            role_map = {} 
            for r_data in local_roles:
                r = Role(id=r_data['id'], name=r_data['name'], description=r_data.get('description'))
                db.session.add(r)
                role_map[r_data['id']] = r
            
            db.session.flush() # Flush to ensure IDs are active
            
            # Roles-Permissions
            for rp in local_roles_permissions:
                role = role_map.get(rp['role_id'])
                perm = perm_map.get(rp['permission_id'])
                if role and perm:
                    # Manually insert into association table to avoid object attach issues
                    db.session.execute(
                        text("INSERT INTO roles_permissions (role_id, permission_id) VALUES (:rid, :pid)"),
                        {'rid': role.id, 'pid': perm.id}
                    )
            
            # Users
            for u_data in local_users:
                u = User(
                    id=u_data['id'],
                    username=u_data['username'],
                    active=bool(u_data['active']),
                    role_id=u_data.get('role_id')
                )
                u.password_hash = u_data['password_hash']
                db.session.add(u)
                
            db.session.commit()
            print("Sync successful!")
            
            # 5. Reset Sequences
            print("Resetting sequences...")
            for table in ['user', 'role', 'permission']:
                try:
                    # Generic postgres sequence reset
                    seq_name = f"{table}_id_seq"
                    sql = text(f"SELECT setval('{seq_name}', (SELECT MAX(id) FROM \"{table}\"));")
                    db.session.execute(sql)
                except Exception as seq_e:
                    print(f"Sequence reset failed for {table}: {seq_e}")
            db.session.commit()
            print("Sequences reset.")
            
        except Exception as e:
            print(f"Error inserting data: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    sync_users()
