"""
为本地SQLite数据库的sale_item表添加缺失的列
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
    # 检查现有列
    cursor.execute("PRAGMA table_info(sale_item)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {columns}\n")
    
    # 添加 unit_price 列
    if 'unit_price' not in columns:
        print("Adding unit_price column...")
        cursor.execute("""
            ALTER TABLE sale_item 
            ADD COLUMN unit_price NUMERIC(10, 2)
        """)
        print("✓ unit_price column added")
    else:
        print("✓ unit_price column already exists")
    
    # 添加 total_amount 列
    if 'total_amount' not in columns:
        print("Adding total_amount column...")
        cursor.execute("""
            ALTER TABLE sale_item 
            ADD COLUMN total_amount NUMERIC(12, 2) DEFAULT 0
        """)
        print("✓ total_amount column added")
    else:
        print("✓ total_amount column already exists")
    
    conn.commit()
    
    # 验证
    cursor.execute("PRAGMA table_info(sale_item)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\nFinal sale_item columns: {columns}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    conn.close()

print("\nDone! Please restart your Flask application.")
