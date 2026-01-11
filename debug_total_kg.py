"""
调试脚本：检查生产环境中Sale对象的total_kg值
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Sale
from app.services.sale_service import SaleService

def debug_sale_total_kg():
    """调试Sale的total_kg"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Debugging Sale total_kg Issue")
        print("=" * 60)
        
        # 获取最新的销售单
        sale = Sale.query.order_by(Sale.sale_time.desc()).first()
        
        if not sale:
            print("No sales found!")
            return
        
        print(f"\nSale ID: {sale.id}")
        print(f"Customer: {sale.customer.name if sale.customer else 'N/A'}")
        print(f"Sale Time: {sale.sale_time}")
        print()
        
        # 检查原始数据库值
        print("Database Values:")
        print(f"  sale.total_kg (raw): {repr(sale.total_kg)}")
        print(f"  sale.total_kg (type): {type(sale.total_kg)}")
        print(f"  sale.total_kg (float): {float(sale.total_kg) if sale.total_kg else 0}")
        print()
        
        # 检查items
        print(f"Items count: {sale.items.count()}")
        for i, item in enumerate(sale.items, 1):
            print(f"  Item {i}:")
            print(f"    spec: {item.spec.name}")
            print(f"    subtotal_kg (raw): {repr(item.subtotal_kg)}")
            print(f"    subtotal_kg (float): {float(item.subtotal_kg)}")
        print()
        
        # 计算总重量
        calculated_total = sum(item.subtotal_kg for item in sale.items)
        print(f"Calculated total_kg: {float(calculated_total)}")
        print()
        
        # 检查to_dict方法
        print("to_dict() output:")
        sale_dict = sale.to_dict(include_items=True)
        print(f"  total_kg: {sale_dict.get('total_kg')}")
        print(f"  total_amount: {sale_dict.get('total_amount')}")
        print()
        
        # 使用SaleService获取
        print("Via SaleService.get_sale_detail():")
        sale_from_service = SaleService.get_sale_detail(sale.id)
        service_dict = sale_from_service.to_dict(include_items=True)
        print(f"  total_kg: {service_dict.get('total_kg')}")
        print(f"  total_amount: {service_dict.get('total_amount')}")

if __name__ == '__main__':
    debug_sale_total_kg()
