"""
在生产环境创建回款记录表
使用环境变量中的DATABASE_URL连接生产数据库
"""
import os
import psycopg2
from urllib.parse import urlparse

def create_remittance_table_production():
    """在生产环境创建remittance表"""
    
    # 从环境变量获取数据库URL
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("错误: 未找到DATABASE_URL环境变量")
        print("请设置环境变量: set DATABASE_URL=your_database_url")
        return
    
    # 解析数据库URL
    result = urlparse(database_url)
    
    try:
        # 连接到生产数据库
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        cursor = conn.cursor()
        
        # 创建remittance表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS remittance (
            id SERIAL PRIMARY KEY,
            remittance_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            sale_id VARCHAR(50) NOT NULL REFERENCES sale(id),
            amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
            notes TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(50) NOT NULL
        );
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        
        print("✓ Remittance table created successfully in production")
        
        # 验证表是否存在
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'remittance'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        if columns:
            print("✓ Remittance table verified in production database")
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        else:
            print("✗ Remittance table not found in production database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Error creating remittance table: {str(e)}")
        raise

if __name__ == '__main__':
    create_remittance_table_production()
