"""
创建采购相关表到Supabase
"""
import os
from app import create_app, db
from app.models import Purchase, PurchaseItem

def create_purchase_tables():
    """在Supabase中创建采购相关表"""
    # 修复DATABASE_URL格式
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    with app.app_context():
        print("=" * 60)
        print("创建采购相关表")
        print("=" * 60)
        
        try:
            # 创建表
            print("\n创建 purchase 和 purchase_item 表...")
            db.create_all()
            
            print("✓ 表创建成功!")
            
            # 验证表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n当前数据库表:")
            for table in sorted(tables):
                print(f"  - {table}")
            
            if 'purchase' in tables and 'purchase_item' in tables:
                print("\n✓ 采购表创建成功!")
            else:
                print("\n✗ 警告: 采购表可能未成功创建")
                
        except Exception as e:
            print(f"\n✗ 错误: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    create_purchase_tables()
