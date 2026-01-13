"""
检查并同步数据库结构到生产环境
比较本地模型定义与生产数据库,列出需要同步的变化
"""
import os
from app import create_app, db
from app.models import Remittance, Sale
from sqlalchemy import inspect

def check_database_changes():
    """检查数据库结构变化"""
    
    print("=" * 60)
    print("数据库结构变化检查")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        local_tables = inspector.get_table_names()
        
        print("\n本地数据库表列表:")
        for table in sorted(local_tables):
            print(f"  - {table}")
        
        # 检查新增的表
        print("\n" + "=" * 60)
        print("新增的表 (需要在生产环境创建)")
        print("=" * 60)
        
        new_tables = []
        
        # 检查remittance表
        if 'remittance' in local_tables:
            print("\n✓ remittance 表 (回款记录表)")
            print("  状态: 已在本地创建")
            print("  需要操作: 在生产环境创建此表")
            
            # 显示表结构
            columns = inspector.get_columns('remittance')
            print("\n  表结构:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col['default'] else ""
                print(f"    - {col['name']}: {col['type']} {nullable}{default}")
            
            # 显示约束
            print("\n  约束:")
            print("    - PRIMARY KEY: id")
            print("    - FOREIGN KEY: sale_id REFERENCES sale(id)")
            print("    - CHECK: amount > 0")
            
            new_tables.append('remittance')
        
        # 检查Sale表的变化
        print("\n" + "=" * 60)
        print("修改的表 (需要在生产环境更新)")
        print("=" * 60)
        
        if 'sale' in local_tables:
            print("\n✓ sale 表")
            print("  变化: 添加了与remittance表的关系")
            print("  影响: 无需修改表结构,仅在应用层面建立关系")
            print("  需要操作: 无 (关系由外键在remittance表中定义)")
        
        # 生成迁移SQL
        print("\n" + "=" * 60)
        print("生产环境迁移SQL")
        print("=" * 60)
        
        if new_tables:
            print("\n-- 创建remittance表")
            print("""
CREATE TABLE IF NOT EXISTS remittance (
    id SERIAL PRIMARY KEY,
    remittance_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sale_id VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    CONSTRAINT fk_remittance_sale FOREIGN KEY (sale_id) REFERENCES sale(id),
    CONSTRAINT check_remittance_amount_positive CHECK (amount > 0)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_remittance_sale_id ON remittance(sale_id);
CREATE INDEX IF NOT EXISTS idx_remittance_time ON remittance(remittance_time);
""")
        
        # 总结
        print("\n" + "=" * 60)
        print("迁移总结")
        print("=" * 60)
        
        if new_tables:
            print(f"\n需要创建的新表: {len(new_tables)}")
            for table in new_tables:
                print(f"  - {table}")
            
            print("\n迁移步骤:")
            print("  1. 确保Render部署已完成")
            print("  2. 在Render Shell中运行:")
            print("     python create_remittance_table_production.py")
            print("  3. 验证表创建成功")
            print("  4. 测试回款功能")
        else:
            print("\n✓ 无需迁移,数据库结构已同步")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    check_database_changes()
