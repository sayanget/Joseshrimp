import sqlite3
import os

db_path = os.path.join('instance', 'jose.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE sale ADD COLUMN discount NUMERIC(12, 2) DEFAULT 0")
    print("Added discount column")
except Exception as e:
    print(f"Error adding discount column: {e}")

try:
    cursor.execute("ALTER TABLE sale ADD COLUMN manual_total_amount NUMERIC(12, 2)")
    print("Added manual_total_amount column")
except Exception as e:
    print(f"Error adding manual_total_amount column: {e}")

conn.commit()
conn.close()
