"""
检查最新创建的销售单
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Sale

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Checking Latest Sales")
    print("=" * 60)
    
    # 获取最新的5条销售单
    sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    
    for sale in sales:
        print(f"\nSale ID: {sale.id}")
        print(f"  Created: {sale.created_at}")
        print(f"  Customer: {sale.customer.name if sale.customer else 'N/A'}")
        print(f"  total_kg (DB): {float(sale.total_kg) if sale.total_kg else 0}")
        print(f"  total_amount (DB): {float(sale.total_amount) if sale.total_amount else 0}")
        print(f"  Items:")
        
        calculated_kg = 0
        for item in sale.items:
            print(f"    - {item.spec.name}: {item.box_qty} boxes × {float(item.spec.kg_per_box)} = {float(item.subtotal_kg)} KG")
            calculated_kg += float(item.subtotal_kg)
        
        print(f"  Calculated total: {calculated_kg} KG")
        
        if float(sale.total_kg) != calculated_kg:
            print(f"  ⚠️  MISMATCH! DB has {float(sale.total_kg)} but should be {calculated_kg}")
        else:
            print(f"  ✓ Values match")
