"""
检查生产数据库中的销售单数据
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Sale

def check_sales_data():
    """检查销售单数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Checking Sales Data in Production")
        print("=" * 60)
        
        # 获取最近的5条销售记录
        sales = Sale.query.order_by(Sale.sale_time.desc()).limit(5).all()
        
        print(f"\nRecent 5 sales records:\n")
        for sale in sales:
            print(f"ID: {sale.id}")
            print(f"  Customer: {sale.customer.name if sale.customer else 'N/A'}")
            print(f"  Payment: {sale.payment_type}")
            print(f"  Total KG (DB): {float(sale.total_kg) if sale.total_kg else 0}")
            print(f"  Total Amount (DB): {float(sale.total_amount) if sale.total_amount else 0}")
            print(f"  Items count: {sale.items.count()}")
            
            # 计算实际总重量
            actual_total_kg = sum(item.subtotal_kg for item in sale.items)
            print(f"  Calculated KG: {float(actual_total_kg)}")
            
            # 检查是否匹配
            if float(sale.total_kg) != float(actual_total_kg):
                print(f"  [WARNING] Mismatch! DB has {float(sale.total_kg)} but should be {float(actual_total_kg)}")
            else:
                print(f"  [OK] Values match")
            print()

if __name__ == '__main__':
    check_sales_data()
