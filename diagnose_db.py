"""
测试数据库连接并显示配置信息
用于在Render上运行以诊断问题
"""
import os
import sys

print("=" * 60)
print("Database Connection Diagnostic")
print("=" * 60)

# 检查环境变量
print("\n1. Environment Variables:")
print(f"   DATABASE_URL exists: {'DATABASE_URL' in os.environ}")
if 'DATABASE_URL' in os.environ:
    db_url = os.environ['DATABASE_URL']
    # 隐藏密码
    if '@' in db_url:
        parts = db_url.split('@')
        user_part = parts[0].split(':')[0]
        host_part = '@'.join(parts[1:])
        print(f"   DATABASE_URL: {user_part}:****@{host_part}")
    else:
        print(f"   DATABASE_URL: {db_url[:50]}...")
else:
    print("   DATABASE_URL: NOT SET")

print(f"   DEV_DATABASE_URL exists: {'DEV_DATABASE_URL' in os.environ}")

# 检查Flask配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    app = create_app()
    
    print("\n2. Flask Configuration:")
    print(f"   Config name: {app.config.get('ENV', 'unknown')}")
    
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')
    if db_uri and db_uri != 'NOT SET':
        if 'sqlite' in db_uri.lower():
            print(f"   Database type: SQLite")
            print(f"   Database URI: {db_uri}")
        elif 'postgres' in db_uri.lower():
            print(f"   Database type: PostgreSQL")
            # 隐藏密码
            if '@' in db_uri:
                parts = db_uri.split('@')
                user_part = parts[0].split(':')[0]
                host_part = '@'.join(parts[1:])
                print(f"   Database URI: {user_part}:****@{host_part}")
        else:
            print(f"   Database URI: {db_uri[:50]}...")
    else:
        print(f"   Database URI: {db_uri}")
    
    # 尝试连接数据库
    print("\n3. Database Connection Test:")
    try:
        from app import db
        with app.app_context():
            # 执行简单查询
            result = db.session.execute(db.text("SELECT 1")).scalar()
            print(f"   ✓ Connection successful! (test query returned: {result})")
            
            # 检查是否是PostgreSQL
            try:
                version = db.session.execute(db.text("SELECT version()")).scalar()
                if 'PostgreSQL' in version:
                    print(f"   ✓ Connected to PostgreSQL")
                    print(f"   Version: {version[:80]}...")
                elif 'SQLite' in version:
                    print(f"   ⚠️  Connected to SQLite (should be PostgreSQL!)")
                    print(f"   Version: {version}")
            except:
                pass
            
            # 检查表
            from app.models import Sale
            sale_count = Sale.query.count()
            print(f"   Total sales in database: {sale_count}")
            
            # 检查最新销售单
            latest = Sale.query.order_by(Sale.created_at.desc()).first()
            if latest:
                print(f"   Latest sale: {latest.id} (created: {latest.created_at})")
            
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        
except Exception as e:
    print(f"\n✗ Error loading app: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
