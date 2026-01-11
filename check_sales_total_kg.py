"""
检查生产环境中销售记录的total_kg值
"""
import os
from app import create_app, db
from app.models import Sale, SaleItem
from datetime import datetime, timedelta
from sqlalchemy import func

def check_sales_data():
    # 修复DATABASE_URL格式
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    with app.app_context():
        print("=" * 60)
        print("检查生产环境销售数据")
        print("=" * 60)
        
        # 获取最近7天的销售记录
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_sales = Sale.query.filter(
            Sale.sale_time >= seven_days_ago,
            Sale.status == 'active'
        ).order_by(Sale.sale_time.desc()).limit(10).all()
        
        print(f"\n最近10条销售记录:")
        print("-" * 60)
        for sale in recent_sales:
            print(f"ID: {sale.id}")
            print(f"  时间: {sale.sale_time}")
            print(f"  客户: {sale.customer.name if sale.customer else 'N/A'}")
            print(f"  total_kg (数据库): {sale.total_kg} (类型: {type(sale.total_kg)})")
            print(f"  total_kg (转float): {float(sale.total_kg)}")
            print(f"  total_amount: {sale.total_amount}")
            
            # 检查明细
            items = sale.items.all()
            print(f"  明细数量: {len(items)}")
            if items:
                total_from_items = sum(float(item.subtotal_kg) for item in items)
                print(f"  从明细计算的总重量: {total_from_items}")
            print()
        
        # 按日期统计
        print("\n按日期统计 (最近7天):")
        print("-" * 60)
        daily_stats = db.session.query(
            func.date(Sale.sale_time).label('date'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_kg).label('total_kg'),
            func.sum(Sale.total_amount).label('total_amount')
        ).filter(
            Sale.sale_time >= seven_days_ago,
            Sale.status == 'active'
        ).group_by(
            func.date(Sale.sale_time)
        ).order_by(
            func.date(Sale.sale_time).desc()
        ).all()
        
        for stat in daily_stats:
            print(f"日期: {stat.date}")
            print(f"  订单数: {stat.count}")
            print(f"  总重量: {stat.total_kg} (类型: {type(stat.total_kg)})")
            print(f"  总金额: {stat.total_amount}")
            print()

if __name__ == "__main__":
    check_sales_data()
