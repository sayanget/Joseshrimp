
import sys
import os
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def migrate_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'sales.db')
    print(f"Migrating database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create memo table
        print("Creating memo table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,                           -- 内容
            memo_date DATE NOT NULL,                         -- 日期
            is_completed BOOLEAN NOT NULL DEFAULT 0,         -- 是否完成
            active BOOLEAN NOT NULL DEFAULT 1,               -- 是否启用（软删除）
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(50) NOT NULL,
            updated_at DATETIME NULL,
            updated_by VARCHAR(50) NULL
        );
        """)
        
        # Create indices
        print("Creating indices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memo_date ON memo(memo_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memo_active ON memo(active);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memo_created_at ON memo(created_at);")
        
        conn.commit()
        print("Migration successful!")
        
    except Exception as e:
        print(f"Error migrating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()
