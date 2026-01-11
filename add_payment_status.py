"""
添加payment_status字段到Sale表
"""
from app import create_app, db
from app.models import Sale
import os

def add_payment_status_field():
    """添加payment_status字段并设置默认值"""
    # 修复DATABASE_URL格式
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("错误: 未设置DATABASE_URL环境变量")
        print("请运行: $env:DATABASE_URL=\"your_connection_string\"")
        return
    
    if db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    with app.app_context():
        print("=" * 60)
        print("添加payment_status字段到Sale表")
        print("=" * 60)
        
        try:
            # 添加列（如果不存在）
            print("\n1. 添加payment_status列...")
            db.session.execute(db.text("""
                ALTER TABLE sale 
                ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) DEFAULT 'unpaid' NOT NULL
            """))
            
            # 更新现有数据：现金销售设为paid，信用销售设为unpaid
            print("2. 更新现有数据...")
            db.session.execute(db.text("""
                UPDATE sale 
                SET payment_status = CASE 
                    WHEN payment_type = '现金' THEN 'paid'
                    ELSE 'unpaid'
                END
                WHERE payment_status IS NULL OR payment_status = ''
            """))
            
            # 添加约束（如果不存在）
            print("3. 添加check约束...")
            try:
                db.session.execute(db.text("""
                    ALTER TABLE sale
                    ADD CONSTRAINT check_payment_status 
                    CHECK (payment_status IN ('unpaid','partial','paid'))
                """))
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print("   约束已存在，跳过")
                else:
                    raise
            
            db.session.commit()
            
            print("\n✓ payment_status字段添加成功!")
            
            # 验证
            print("\n4. 验证数据...")
            result = db.session.execute(db.text("""
                SELECT payment_type, payment_status, COUNT(*) as count
                FROM sale
                WHERE status = 'active'
                GROUP BY payment_type, payment_status
                ORDER BY payment_type, payment_status
            """))
            
            print("\n当前数据分布:")
            for row in result:
                print(f"  {row[0]}: {row[1]} - {row[2]}条记录")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 错误: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_payment_status_field()
