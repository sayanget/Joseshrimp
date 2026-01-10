"""
为本地SQLite数据库的sale_item表添加product_id列
"""
import sqlite3
import os

db_path = 'sales.db'

if not os.path.exists(db_path):
    print(f"Error: Database file {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 检查列是否已存在
    cursor.execute("PRAGMA table_info(sale_item)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'product_id' in columns:
        print("✓ product_id column already exists in sale_item table")
    else:
        print("Adding product_id column to sale_item table...")
        cursor.execute("""
            ALTER TABLE sale_item 
            ADD COLUMN product_id INTEGER REFERENCES product(id)
        """)
        conn.commit()
        print("✓ product_id column added successfully!")
    
    # 验证
    cursor.execute("PRAGMA table_info(sale_item)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\nCurrent sale_item columns: {columns}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nDone!")
