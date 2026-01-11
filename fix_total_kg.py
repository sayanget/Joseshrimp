"""
修复生产环境中所有销售记录的total_kg值
从SaleItem的subtotal_kg重新计算
"""
import os
from app import create_app, db
from app.models import Sale, SaleItem
from sqlalchemy import func

def recalculate_all_total_kg():
    """重新计算所有销售记录的total_kg"""
    # 修复DATABASE_URL格式
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    with app.app_context():
        print("=" * 60)
        print("开始重新计算所有销售记录的total_kg")
        print("=" * 60)
        
        # 获取所有活跃的销售记录
        sales = Sale.query.filter_by(status='active').all()
        print(f"\n找到 {len(sales)} 条活跃销售记录")
        
        updated_count = 0
        error_count = 0
        
        for sale in sales:
            try:
                # 从SaleItem计算总重量
                total = db.session.query(func.sum(SaleItem.subtotal_kg))\
                    .filter(SaleItem.sale_id == sale.id).scalar() or 0
                
                old_value = float(sale.total_kg)
                new_value = float(total)
                
                if old_value != new_value:
                    print(f"\n更新 {sale.id}:")
                    print(f"  旧值: {old_value} KG")
                    print(f"  新值: {new_value} KG")
                    print(f"  差异: {new_value - old_value} KG")
                    
                    sale.total_kg = total
                    updated_count += 1
                else:
                    print(f"✓ {sale.id}: 已正确 ({new_value} KG)")
                    
            except Exception as e:
                print(f"✗ 错误处理 {sale.id}: {str(e)}")
                error_count += 1
        
        # 提交更改
        if updated_count > 0:
            print(f"\n准备提交 {updated_count} 条更新...")
            try:
                db.session.commit()
                print("✓ 提交成功!")
            except Exception as e:
                print(f"✗ 提交失败: {str(e)}")
                db.session.rollback()
                return
        else:
            print("\n没有需要更新的记录")
        
        print("\n" + "=" * 60)
        print(f"完成! 更新: {updated_count}, 错误: {error_count}")
        print("=" * 60)

if __name__ == "__main__":
    recalculate_all_total_kg()
