"""
更新现有销售单的total_kg字段
用于修复生产环境中总重量显示为0的问题
"""
import os
import sys
from decimal import Decimal

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Sale, SaleItem

def update_total_kg():
    """更新所有销售单的total_kg"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Updating total_kg for existing sales records")
        print("=" * 60)
        
        # 获取所有销售单
        sales = Sale.query.all()
        print(f"\nFound {len(sales)} sales records")
        
        updated_count = 0
        for sale in sales:
            # 计算总重量
            total_kg = sum(item.subtotal_kg for item in sale.items)
            
            # 只更新total_kg为0或与计算值不同的记录
            if sale.total_kg != total_kg:
                old_value = float(sale.total_kg) if sale.total_kg else 0
                sale.total_kg = total_kg
                updated_count += 1
                print(f"  Updated {sale.id}: {old_value} -> {float(total_kg)} KG")
        
        if updated_count > 0:
            db.session.commit()
            print(f"\n[OK] Successfully updated {updated_count} sales records")
        else:
            print("\n[OK] All sales records already have correct total_kg")
        
        print("\nDone!")

if __name__ == '__main__':
    update_total_kg()
