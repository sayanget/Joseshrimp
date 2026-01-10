"""
数据库迁移脚本: 添加商品管理功能

1. 创建 product 表
2. 为 sale_item 表添加 product_id 字段
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def migrate_add_product_table():
    """添加商品表和相关字段"""
    
    # 获取数据库URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("For local: use SQLite")
        print("For production: set DATABASE_URL=postgresql://...")
        sys.exit(1)
    
    # 修正postgres://为postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    print(f"Connecting to database...")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            # 1. 创建product表
            if 'product' not in existing_tables:
                print("\n1. Creating product table...")
                conn.execute(text("""
                    CREATE TABLE product (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        cash_price NUMERIC(10, 2) NOT NULL CHECK (cash_price > 0),
                        credit_price NUMERIC(10, 2) NOT NULL CHECK (credit_price > 0),
                        active BOOLEAN DEFAULT TRUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        created_by VARCHAR(50) NOT NULL,
                        updated_at TIMESTAMP,
                        updated_by VARCHAR(50)
                    )
                """))
                conn.commit()
                print("   ✓ Product table created")
            else:
                print("\n1. Product table already exists")
            
            # 2. 为sale_item表添加product_id字段
            sale_item_columns = [c['name'] for c in inspector.get_columns('sale_item')]
            
            if 'product_id' not in sale_item_columns:
                print("\n2. Adding product_id to sale_item table...")
                conn.execute(text("""
                    ALTER TABLE sale_item 
                    ADD COLUMN product_id INTEGER REFERENCES product(id)
                """))
                conn.commit()
                print("   ✓ product_id column added")
            else:
                print("\n2. product_id column already exists in sale_item")
            
            # 验证
            print("\n=== Verification ===")
            if 'product' in inspector.get_table_names():
                product_columns = [c['name'] for c in inspector.get_columns('product')]
                print(f"Product table columns: {product_columns}")
            
            sale_item_columns = [c['name'] for c in inspector.get_columns('sale_item')]
            if 'product_id' in sale_item_columns:
                print("✓ sale_item.product_id exists")
            
            print("\n✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add Product Management")
    print("=" * 60)
    migrate_add_product_table()
    print("=" * 60)
