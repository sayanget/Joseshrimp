import sqlite3
import os
from app import create_app, db
from sqlalchemy import text

def simple_sync():
    print("简化用户同步...")
    
    # 1. 读取本地数据
    conn = sqlite3.connect('instance/sales.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM permission")
    permissions = [dict(row) for row in cur.fetchall()]
    
    cur.execute("SELECT * FROM role")
    roles = [dict(row) for row in cur.fetchall()]
    
    cur.execute("SELECT * FROM user")
    users = [dict(row) for row in cur.fetchall()]
    
    cur.execute("SELECT * FROM roles_permissions")
    roles_perms = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    
    print(f"读取: {len(users)} 用户, {len(roles)} 角色, {len(permissions)} 权限")

    # 2. 连接生产数据库
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        # 3. 删除旧表
        print("删除旧表...")
        db.session.execute(text('DROP TABLE IF EXISTS roles_permissions CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS role CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS permission CASCADE'))
        db.session.commit()
        
        # 4. 创建新表
        print("创建新表...")
        db.create_all()
        
        # 5. 插入数据（不包含时间戳字段）
        print("插入数据...")
        
        # Permissions
        for p in permissions:
            db.session.execute(
                text("INSERT INTO permission (id, name, description) VALUES (:id, :name, :desc)"),
                {'id': p['id'], 'name': p['name'], 'desc': p.get('description')}
            )
        
        # Roles
        for r in roles:
            db.session.execute(
                text("INSERT INTO role (id, name, description) VALUES (:id, :name, :desc)"),
                {'id': r['id'], 'name': r['name'], 'desc': r.get('description')}
            )
        
        # Roles-Permissions
        for rp in roles_perms:
            db.session.execute(
                text("INSERT INTO roles_permissions (role_id, permission_id) VALUES (:rid, :pid)"),
                {'rid': rp['role_id'], 'pid': rp['permission_id']}
            )
        
        # Users - 只插入必需字段，让数据库使用默认值
        for u in users:
            db.session.execute(
                text("""
                    INSERT INTO "user" (id, username, password_hash, active, role_id)
                    VALUES (:id, :u, :p, :a, :r)
                """),
                {
                    'id': u['id'],
                    'u': u['username'],
                    'p': u['password_hash'],
                    'a': bool(u['active']),
                    'r': u['role_id']
                }
            )
        
        db.session.commit()
        print("同步成功！")
        
        # 重置序列
        for table in ['user', 'role', 'permission']:
            try:
                db.session.execute(text(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM \"{table}\"))"))
            except:
                pass
        db.session.commit()

if __name__ == "__main__":
    simple_sync()
