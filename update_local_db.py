
import sqlite3

def update_db():
    db_path = 'instance/sales.db'
    print(f"Updating {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Check if column exists first
        cursor.execute("PRAGMA table_info(sale)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'payment_status' not in columns:
            print("Adding payment_status column...")
            cursor.execute("ALTER TABLE sale ADD COLUMN payment_status VARCHAR(20) DEFAULT 'unpaid' NOT NULL")
            print("Column added.")
            
            print("Updating existing records...")
            cursor.execute("UPDATE sale SET payment_status = 'paid' WHERE payment_type = '现金'")
            cursor.execute("UPDATE sale SET payment_status = 'unpaid' WHERE payment_type != '现金'")
            conn.commit()
            print("Records updated.")
        else:
            print("Column already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    update_db()
