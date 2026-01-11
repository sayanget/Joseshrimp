"""
修复生产环境中所有销售记录的total_kg值
从SaleItem的subtotal_kg重新计算

使用方法:
1. 在Render Dashboard中找到DATABASE_URL环境变量的值
2. 运行: set DATABASE_URL=你的数据库连接字符串
3. 运行: python fix_total_kg_simple.py
"""
import os
import sys

def main():
    # 提示用户输入DATABASE_URL
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("=" * 60)
        print("需要设置DATABASE_URL环境变量")
        print("=" * 60)
        print("\n请从Render Dashboard复制DATABASE_URL，然后运行:")
        print("  set DATABASE_URL=你的连接字符串")
        print("  python fix_total_kg_simple.py")
        print("\n或者直接在这里输入DATABASE_URL:")
        db_url = input("DATABASE_URL: ").strip()
        
        if not db_url:
            print("错误: 必须提供DATABASE_URL")
            sys.exit(1)
        
        os.environ['DATABASE_URL'] = db_url
    
    # 修复postgres://为postgresql://
    if db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)
        print("已自动修正DATABASE_URL格式 (postgres:// -> postgresql://)")
    
    print(f"\n连接到数据库: {db_url[:50]}...")
    
    # 导入并运行修复逻辑
    from app import create_app, db
    from app.models import Sale, SaleItem
    from sqlalchemy import func
    
    app = create_app('production')
    with app.app_context():
        print("\n" + "=" * 60)
        print("开始重新计算所有销售记录的total_kg")
        print("=" * 60)
        
        # 获取所有活跃的销售记录
        sales = Sale.query.filter_by(status='active').all()
        print(f"\n找到 {len(sales)} 条活跃销售记录")
        
        if len(sales) == 0:
            print("没有需要处理的销售记录")
            return
        
        # 询问用户确认
        print(f"\n将重新计算这 {len(sales)} 条记录的total_kg值")
        confirm = input("确认继续? (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("操作已取消")
            return
        
        updated_count = 0
        error_count = 0
        
        print("\n开始处理...")
        for i, sale in enumerate(sales, 1):
            try:
                # 从SaleItem计算总重量
                total = db.session.query(func.sum(SaleItem.subtotal_kg))\
                    .filter(SaleItem.sale_id == sale.id).scalar() or 0
                
                old_value = float(sale.total_kg)
                new_value = float(total)
                
                if old_value != new_value:
                    print(f"\n[{i}/{len(sales)}] 更新 {sale.id}:")
                    print(f"  旧值: {old_value} KG")
                    print(f"  新值: {new_value} KG")
                    print(f"  差异: {new_value - old_value:+.3f} KG")
                    
                    sale.total_kg = total
                    updated_count += 1
                else:
                    if i % 10 == 0:  # 每10条显示一次进度
                        print(f"[{i}/{len(sales)}] 处理中...")
                    
            except Exception as e:
                print(f"\n✗ 错误处理 {sale.id}: {str(e)}")
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
        print(f"完成! 更新: {updated_count}, 错误: {error_count}, 总计: {len(sales)}")
        print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
