"""
回填现有销售记录的价格和金额

用途：为已存在的销售记录添加价格信息
- 根据支付方式和当前系统价格设置unit_price
- 计算所有item的total_amount
- 计算sale的total_amount
"""

from app import create_app, db
from app.models import Sale, SaleItem, SystemConfig
from decimal import Decimal

def backfill_prices():
    """回填价格到现有销售记录"""
    app = create_app('development')
    
    with app.app_context():
        # 获取当前价格
        cash_price = SystemConfig.get_value('price_cash', value_type=float)
        credit_price = SystemConfig.get_value('price_credit', value_type=float)
        
        if not cash_price or not credit_price:
            print("错误：系统价格未设置")
            return
        
        print(f"当前价格设置：")
        print(f"  现金价: ${cash_price}/KG")
        print(f"  信用价: ${credit_price}/KG")
        print()
        
        # 查找所有没有价格的销售项
        items_without_price = SaleItem.query.filter(
            (SaleItem.unit_price == None) | (SaleItem.unit_price == 0)
        ).all()
        
        print(f"找到 {len(items_without_price)} 个需要回填价格的销售项")
        
        updated_sales = set()
        
        for item in items_without_price:
            sale = item.sale
            
            # 根据支付方式设置价格
            if sale.payment_type == '现金':
                item.unit_price = Decimal(str(cash_price))
            elif sale.payment_type == 'Crédito':
                item.unit_price = Decimal(str(credit_price))
            else:
                print(f"警告：未知支付方式 {sale.payment_type} for sale {sale.id}")
                continue
            
            # 计算item金额
            item.total_amount = item.subtotal_kg * item.unit_price
            updated_sales.add(sale.id)
        
        # 更新所有受影响的销售单总金额
        print(f"\n更新 {len(updated_sales)} 个销售单的总金额...")
        
        for sale_id in updated_sales:
            sale = Sale.query.get(sale_id)
            sale.total_amount = sum(item.total_amount for item in sale.items)
        
        db.session.commit()
        
        print(f"\n✓ 回填完成！")
        print(f"  更新了 {len(items_without_price)} 个销售项")
        print(f"  更新了 {len(updated_sales)} 个销售单")

if __name__ == "__main__":
    backfill_prices()
