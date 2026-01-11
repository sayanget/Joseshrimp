"""
检查并更新所有销售单的total_kg
特别关注total_kg为0的记录
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Sale

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Checking and Updating Sales with total_kg = 0")
    print("=" * 60)
    
    # 查找所有total_kg为0的销售单
    sales_with_zero = Sale.query.filter(Sale.total_kg == 0).all()
    
    print(f"\nFound {len(sales_with_zero)} sales with total_kg = 0")
    
    if not sales_with_zero:
        print("All sales have correct total_kg!")
        exit(0)
    
    print("\nUpdating sales:")
    print("-" * 60)
    
    for sale in sales_with_zero:
        # 计算正确的total_kg
        total_kg = sum(item.subtotal_kg for item in sale.items)
        
        print(f"Sale {sale.id}:")
        print(f"  Current total_kg: {float(sale.total_kg)}")
        print(f"  Calculated total_kg: {float(total_kg)}")
        print(f"  Items: {sale.items.count()}")
        
        # 更新
        sale.total_kg = total_kg
        print(f"  -> Updated to {float(total_kg)}")
        print()
    
    # 提交更改
    db.session.commit()
    print("=" * 60)
    print(f"Successfully updated {len(sales_with_zero)} sales!")
    print("=" * 60)
    
    # 验证
    print("\nVerification:")
    remaining_zero = Sale.query.filter(Sale.total_kg == 0).count()
    print(f"Sales with total_kg = 0: {remaining_zero}")
    
    if remaining_zero == 0:
        print("All sales now have correct total_kg!")
