"""
创建回款记录表
"""
from app import create_app, db
from app.models import Remittance

def create_remittance_table():
    """创建remittance表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 创建表
            db.create_all()
            print("✓ Remittance table created successfully")
            
            # 验证表是否存在
            inspector = db.inspect(db.engine)
            if 'remittance' in inspector.get_table_names():
                print("✓ Remittance table verified in database")
                
                # 显示表结构
                columns = inspector.get_columns('remittance')
                print("\nTable structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("✗ Remittance table not found in database")
                
        except Exception as e:
            print(f"✗ Error creating remittance table: {str(e)}")
            raise

if __name__ == '__main__':
    create_remittance_table()
