
import sqlite3

def check_db(db_path):
    print(f"Checking {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(sale)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Columns in 'sale' table: {column_names}")
        if 'payment_status' in column_names:
            print("✓ payment_status column exists")
        else:
            print("✗ payment_status column MISSING")
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {e}")

if __name__ == "__main__":
    check_db('sales.db')
    check_db('instance/sales.db')
