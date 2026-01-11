"""
初始化本地SQLite数据库（包含采购表）
"""
from app import create_app, db

def init_local_db():
    """初始化本地数据库"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 60)
        print("初始化本地数据库")
        print("=" * 60)
        
        try:
            # 创建所有表
            print("\n创建数据库表...")
            db.create_all()
            
            print("✓ 数据库表创建成功!")
            
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
    init_local_db()
