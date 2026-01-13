
import os
import psycopg2
from urllib.parse import urlparse

def migrate_supabase():
    print("=" * 50)
    print("   Supabase Schema Migration: Add Memo Table")
    print("=" * 50)
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL environment variable not set.")
        print("Please set DATABASE_URL to your Supabase connection string.")
        return

    # Adapt Render/Supabase URL format
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        print("Connecting to database...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("Creating memo table in PostgreSQL...")
        # PostgreSQL syntax
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memo (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            memo_date DATE NOT NULL,
            is_completed BOOLEAN NOT NULL DEFAULT FALSE,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(50) NOT NULL,
            updated_at TIMESTAMP NULL,
            updated_by VARCHAR(50) NULL
        );
        """)
        
        print("Creating indices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memo_date ON memo(memo_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memo_active ON memo(active);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memo_created_at ON memo(created_at);")
        
        conn.commit()
        print("Migration successful! 'memo' table created.")
        
    except Exception as e:
        print(f"Error migrating database: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    migrate_supabase()
