"""
修复数据库schema问题 - 确保所有price字段存在
"""
import os
from app import create_app, db
from sqlalchemy import text, inspect

def fix_database():
    """检查并修复数据库schema"""
    app = create_app('development')
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # 检查sale表
        print("Checking sale table...")
        sale_columns = [c['name'] for c in inspector.get_columns('sale')]
        print(f"Current columns: {sale_columns}")
        
        if 'total_amount' not in sale_columns:
            print("Adding total_amount to sale table...")
            db.session.execute(text("""
                ALTER TABLE sale 
                ADD COLUMN total_amount DECIMAL(12, 2) DEFAULT 0 NOT NULL
            """))
            db.session.commit()
            print("✓ Added total_amount")
        else:
            print("✓ total_amount already exists")
        
        # 检查sale_item表
        print("\nChecking sale_item table...")
        item_columns = [c['name'] for c in inspector.get_columns('sale_item')]
        print(f"Current columns: {item_columns}")
        
        if 'unit_price' not in item_columns:
            print("Adding unit_price to sale_item table...")
            db.session.execute(text("""
                ALTER TABLE sale_item 
                ADD COLUMN unit_price DECIMAL(10, 2)
            """))
            db.session.commit()
            print("✓ Added unit_price")
        else:
            print("✓ unit_price already exists")
            
        if 'total_amount' not in item_columns:
            print("Adding total_amount to sale_item table...")
            db.session.execute(text("""
                ALTER TABLE sale_item 
                ADD COLUMN total_amount DECIMAL(12, 2) DEFAULT 0 NOT NULL
            """))
            db.session.commit()
            print("✓ Added total_amount")
        else:
            print("✓ total_amount already exists")
        
        print("\n✓ Database schema check complete!")

if __name__ == "__main__":
    fix_database()
