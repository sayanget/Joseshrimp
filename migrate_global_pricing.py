"""
数据库迁移脚本：全局定价系统

用途：
1. 创建 system_config 表
2. 从 spec 表移除 cash_price 和 credit_price 字段
3. 初始化默认价格配置

使用方法：
    python migrate_global_pricing.py
"""

import os
import sys
from app import create_app, db
from app.models import SystemConfig
from sqlalchemy import text

def migrate_local():
    """本地SQLite迁移"""
    print("Migrating local database to global pricing system...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # 1. 创建 system_config 表
            print("Creating system_config table...")
            db.create_all()
            
            # 2. 从 spec 表移除价格字段（SQLite不支持DROP COLUMN，需要重建表）
            print("Note: SQLite doesn't support DROP COLUMN")
            print("Price fields in spec table will remain but won't be used")
            
            # 3. 初始化默认价格配置
            print("Initializing default price configuration...")
            SystemConfig.set_value(
                'price_cash',
                '0.50',
                description='现金支付价格 ($/KG)',
                updated_by='system'
            )
            SystemConfig.set_value(
                'price_credit',
                '0.55',
                description='信用支付价格 ($/KG)',
                updated_by='system'
            )
            
            print("✓ Local database migration completed successfully!")
            print("  - Cash price: $0.50/KG")
            print("  - Credit price: $0.55/KG")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

def migrate_production():
    """生产Supabase迁移"""
    print("Migrating production database to global pricing system...")
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    if db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)
    
    app = create_app('production')
    
    with app.app_context():
        try:
            # 1. 创建 system_config 表
            print("Creating system_config table...")
            db.session.execute(text("""
                CREATE TABLE IF NOT EXISTS system_config (
                    key VARCHAR(50) PRIMARY KEY,
                    value TEXT NOT NULL,
                    description VARCHAR(200),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by VARCHAR(50)
                )
            """))
            
            # 2. 从 spec 表移除价格字段
            print("Removing price fields from spec table...")
            db.session.execute(text("""
                ALTER TABLE spec 
                DROP COLUMN IF EXISTS cash_price
            """))
            db.session.execute(text("""
                ALTER TABLE spec 
                DROP COLUMN IF EXISTS credit_price
            """))
            
            # 3. 初始化默认价格配置
            print("Initializing default price configuration...")
            db.session.execute(text("""
                INSERT INTO system_config (key, value, description, updated_by)
                VALUES 
                    ('price_cash', '0.50', '现金支付价格 ($/KG)', 'system'),
                    ('price_credit', '0.55', '信用支付价格 ($/KG)', 'system')
                ON CONFLICT (key) DO NOTHING
            """))
            
            db.session.commit()
            print("✓ Production database migration completed successfully!")
            print("  - Cash price: $0.50/KG")
            print("  - Credit price: $0.55/KG")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'production':
        migrate_production()
    else:
        migrate_local()
