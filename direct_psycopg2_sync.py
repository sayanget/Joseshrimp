import sqlite3
import psycopg2

# 读取本地数据
print("读取本地数据...")
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

print(f"读取完成: {len(users)} 用户, {len(roles)} 角色, {len(permissions)} 权限")

# 连接Supabase
print("连接Supabase...")
pg_conn = psycopg2.connect(
    "postgresql://postgres.wvhhswzelfpvllzqotxy:QvbU5t0d8sB4rW7P@aws-0-us-west-2.pooler.supabase.com:6543/postgres"
)
pg_cur = pg_conn.cursor()

# 删除旧表
print("删除旧表...")
pg_cur.execute('DROP TABLE IF EXISTS roles_permissions CASCADE')
pg_cur.execute('DROP TABLE IF EXISTS "user" CASCADE')
pg_cur.execute('DROP TABLE IF EXISTS role CASCADE')
pg_cur.execute('DROP TABLE IF EXISTS permission CASCADE')
pg_conn.commit()

# 创建新表
print("创建新表...")
pg_cur.execute("""
    CREATE TABLE permission (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        description VARCHAR(200)
    )
""")

pg_cur.execute("""
    CREATE TABLE role (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        description VARCHAR(200)
    )
""")

pg_cur.execute("""
    CREATE TABLE "user" (
        id SERIAL PRIMARY KEY,
        username VARCHAR(64) UNIQUE NOT NULL,
        password_hash VARCHAR(255),
        active BOOLEAN DEFAULT TRUE NOT NULL,
        role_id INTEGER REFERENCES role(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        last_login TIMESTAMP
    )
""")

pg_cur.execute("""
    CREATE TABLE roles_permissions (
        role_id INTEGER REFERENCES role(id),
        permission_id INTEGER REFERENCES permission(id),
        PRIMARY KEY (role_id, permission_id)
    )
""")

pg_conn.commit()

# 插入数据
print("插入数据...")

for p in permissions:
    pg_cur.execute(
        "INSERT INTO permission (id, name, description) VALUES (%s, %s, %s)",
        (p['id'], p['name'], p.get('description'))
    )

for r in roles:
    pg_cur.execute(
        "INSERT INTO role (id, name, description) VALUES (%s, %s, %s)",
        (r['id'], r['name'], r.get('description'))
    )

for rp in roles_perms:
    pg_cur.execute(
        "INSERT INTO roles_permissions (role_id, permission_id) VALUES (%s, %s)",
        (rp['role_id'], rp['permission_id'])
    )

for u in users:
    pg_cur.execute(
        'INSERT INTO "user" (id, username, password_hash, active, role_id) VALUES (%s, %s, %s, %s, %s)',
        (u['id'], u['username'], u['password_hash'], bool(u['active']), u['role_id'])
    )

pg_conn.commit()

# 重置序列
print("重置序列...")
for table in ['user', 'role', 'permission']:
    pg_cur.execute(f"SELECT setval('{table}_id_seq', (SELECT MAX(id) FROM \"{table}\"))")
pg_conn.commit()

pg_cur.close()
pg_conn.close()

print("同步完成！")
