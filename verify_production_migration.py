"""
验证Supabase生产环境迁移

用途：验证pricing system的数据库迁移是否成功
"""

import os
from app import create_app, db
from app.models import SystemConfig
from sqlalchemy import text, inspect

def verify_production():
    """验证生产环境迁移"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    if db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)
    
    app = create_app('production')
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # 1. 检查system_config表
            print("1. Checking system_config table...")
            if 'system_config' in inspector.get_table_names():
                print("   ✓ system_config table exists")
                
                # 检查配置
                cash_price = SystemConfig.get_value('price_cash')
                credit_price = SystemConfig.get_value('price_credit')
                print(f"   ✓ Cash price: ${cash_price}/KG")
                print(f"   ✓ Credit price: ${credit_price}/KG")
            else:
                print("   ✗ system_config table NOT found")
                return False
            
            # 2. 检查sale表
            print("\n2. Checking sale table...")
            sale_columns = [c['name'] for c in inspector.get_columns('sale')]
            if 'total_amount' in sale_columns:
                print("   ✓ sale.total_amount field exists")
            else:
                print("   ✗ sale.total_amount field NOT found")
                return False
            
            # 3. 检查sale_item表
            print("\n3. Checking sale_item table...")
            item_columns = [c['name'] for c in inspector.get_columns('sale_item')]
            if 'unit_price' in item_columns:
                print("   ✓ sale_item.unit_price field exists")
            else:
                print("   ✗ sale_item.unit_price field NOT found")
                return False
            
            if 'total_amount' in item_columns:
                print("   ✓ sale_item.total_amount field exists")
            else:
                print("   ✗ sale_item.total_amount field NOT found")
                return False
            
            print("\n" + "="*50)
            print("✓ All migration checks passed!")
            print("="*50)
            return True
            
        except Exception as e:
            print(f"\n✗ Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = verify_production()
    exit(0 if success else 1)
