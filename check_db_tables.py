
import sqlite3
import os

def check_db():
    db_path = 'instance/sales.db'
    print(f"Checking database: {os.path.abspath(db_path)}")
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables found:")
        found_memo = False
        for table in tables:
            print(f" - {table[0]}")
            if table[0] == 'memo':
                found_memo = True
        
        if found_memo:
            print("\nSUCCESS: 'memo' table exists.")
        else:
            print("\nFAILURE: 'memo' table NOT found.")
            
    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_db()
