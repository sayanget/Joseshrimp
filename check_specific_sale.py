"""
检查特定销售单 SALE-20260110-014
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Sale

app = create_app()

with app.app_context():
    sale_id = 'SALE-20260110-014'
    
    print("=" * 60)
    print(f"Checking Sale: {sale_id}")
    print("=" * 60)
    
    sale = Sale.query.get(sale_id)
    
    if not sale:
        print(f"\n❌ Sale {sale_id} not found in database!")
        print("\nSearching for sales created today...")
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        today_sales = Sale.query.filter(
            db.func.date(Sale.created_at) == today
        ).order_by(Sale.created_at.desc()).all()
        
        print(f"\nFound {len(today_sales)} sales created today:")
        for s in today_sales:
            print(f"  - {s.id} (created: {s.created_at})")
        exit(1)
    
    print(f"\n✓ Sale found!")
    print(f"\nBasic Info:")
    print(f"  ID: {sale.id}")
    print(f"  Customer: {sale.customer.name if sale.customer else 'N/A'}")
    print(f"  Payment: {sale.payment_type}")
    print(f"  Created: {sale.created_at}")
    print(f"  Created by: {sale.created_by}")
    
    print(f"\nDatabase Values:")
    print(f"  total_kg: {sale.total_kg} (type: {type(sale.total_kg).__name__})")
    print(f"  total_kg (float): {float(sale.total_kg) if sale.total_kg else 0}")
    print(f"  total_amount: {float(sale.total_amount) if sale.total_amount else 0}")
    
    print(f"\nItems ({sale.items.count()}):")
    calculated_kg = 0
    for i, item in enumerate(sale.items, 1):
        print(f"  {i}. {item.spec.name}:")
        print(f"     Box qty: {item.box_qty}")
        print(f"     KG per box: {float(item.spec.kg_per_box)}")
        print(f"     Extra KG: {float(item.extra_kg)}")
        print(f"     Subtotal KG: {float(item.subtotal_kg)}")
        calculated_kg += float(item.subtotal_kg)
    
    print(f"\n  Calculated total: {calculated_kg} KG")
    
    print(f"\nComparison:")
    print(f"  DB total_kg: {float(sale.total_kg) if sale.total_kg else 0}")
    print(f"  Calculated: {calculated_kg}")
    
    if float(sale.total_kg) != calculated_kg:
        print(f"\n⚠️  MISMATCH DETECTED!")
        print(f"  Difference: {calculated_kg - float(sale.total_kg)} KG")
        
        # 尝试修复
        print(f"\nAttempting to fix...")
        sale.total_kg = calculated_kg
        db.session.commit()
        print(f"✓ Updated total_kg to {calculated_kg}")
    else:
        print(f"\n✓ Values match - no fix needed")
