"""
确保Supabase中所有表都存在
"""
import os
from app import create_app, db

def ensure_all_tables():
    """确保所有表都存在于Supabase"""
    # 修复DATABASE_URL格式
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("错误: 未设置DATABASE_URL环境变量")
        print("请运行: $env:DATABASE_URL=\"your_supabase_connection_string\"")
        return
    
    if db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    with app.app_context():
        print("=" * 60)
        print("检查并创建所有数据库表")
        print("=" * 60)
        
        try:
            # 创建所有表（如果不存在）
            print("\n创建所有表...")
            db.create_all()
            
            print("✓ 表创建/验证成功!")
            
            # 验证表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n当前数据库中的表 (共{len(tables)}个):")
            for table in sorted(tables):
                print(f"  ✓ {table}")
            
            # 检查关键表
            required_tables = ['user', 'product', 'purchase', 'purchase_item', 'sale', 'sale_item', 'stock_move']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print(f"\n⚠ 警告: 缺少以下关键表: {', '.join(missing_tables)}")
            else:
                print("\n✓ 所有关键表都已存在!")
                
        except Exception as e:
            print(f"\n✗ 错误: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    ensure_all_tables()
