"""
为instance/sales.db添加product_id列
"""
import sqlite3
import os

db_path = 'instance/sales.db'

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
    
    # 添加 product_id 列
    if 'product_id' not in columns:
        print("Adding product_id column...")
        cursor.execute("""
            ALTER TABLE sale_item 
            ADD COLUMN product_id INTEGER REFERENCES product(id)
        """)
        conn.commit()
        print("✓ product_id column added successfully!")
    else:
        print("✓ product_id column already exists")
    
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
