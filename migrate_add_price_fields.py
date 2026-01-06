"""
数据库迁移脚本：添加双价格系统字段

用途：
1. 为 spec 表添加 cash_price 和 credit_price 字段
2. 为 sale_item 表添加 unit_price 和 total_amount 字段

使用方法：
    # 本地SQLite
    python add_price_fields_local.py
    
    # 生产Supabase
    export DATABASE_URL="postgresql://..."
    python add_price_fields_production.py
"""

import os
import sys
from app import create_app, db
from sqlalchemy import text

def add_price_fields_local():
    """为本地SQLite数据库添加价格字段"""
    print("Adding price fields to local database...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # 为 spec 表添加字段
            print("Adding cash_price and credit_price to spec table...")
            db.session.execute(text("""
                ALTER TABLE spec 
                ADD COLUMN cash_price DECIMAL(10, 2)
            """))
            db.session.execute(text("""
                ALTER TABLE spec 
                ADD COLUMN credit_price DECIMAL(10, 2)
            """))
            
            # 为 sale_item 表添加字段
            print("Adding unit_price and total_amount to sale_item table...")
            db.session.execute(text("""
                ALTER TABLE sale_item 
                ADD COLUMN unit_price DECIMAL(10, 2)
            """))
            db.session.execute(text("""
                ALTER TABLE sale_item 
                ADD COLUMN total_amount DECIMAL(12, 2) DEFAULT 0 NOT NULL
            """))
            
            # 为 sale 表添加字段
            print("Adding total_amount to sale table...")
            db.session.execute(text("""
                ALTER TABLE sale 
                ADD COLUMN total_amount DECIMAL(12, 2) DEFAULT 0 NOT NULL
            """))
            
            db.session.commit()
            print("✓ Local database migration completed successfully!")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

def add_price_fields_production():
    """为生产Supabase数据库添加价格字段"""
    print("Adding price fields to production database...")
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    if db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)
    
    app = create_app('production')
    
    with app.app_context():
        try:
            # 为 spec 表添加字段
            print("Adding cash_price and credit_price to spec table...")
            db.session.execute(text("""
                ALTER TABLE spec 
                ADD COLUMN IF NOT EXISTS cash_price NUMERIC(10, 2)
            """))
            db.session.execute(text("""
                ALTER TABLE spec 
                ADD COLUMN IF NOT EXISTS credit_price NUMERIC(10, 2)
            """))
            
            # 为 sale_item 表添加字段
            print("Adding unit_price and total_amount to sale_item table...")
            db.session.execute(text("""
                ALTER TABLE sale_item 
                ADD COLUMN IF NOT EXISTS unit_price NUMERIC(10, 2)
            """))
            db.session.execute(text("""
                ALTER TABLE sale_item 
                ADD COLUMN IF NOT EXISTS total_amount NUMERIC(12, 2) DEFAULT 0 NOT NULL
            """))
            
            db.session.commit()
            print("✓ Production database migration completed successfully!")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'production':
        add_price_fields_production()
    else:
        add_price_fields_local()
