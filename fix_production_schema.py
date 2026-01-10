"""
Fix production database schema - Add missing total_amount field to sale table

This script is specifically for fixing the missing total_amount column issue in production
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def fix_production_database():
    """Check and fix production database schema"""
    
    # Get database URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        print("Please set it first:")
        print("  set DATABASE_URL=postgresql://...")
        sys.exit(1)
    
    # Fix postgres:// to postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        print("Fixed database URL format")
    
    print(f"Connecting to production database...")
    print(f"Database: {db_url.split('@')[1] if '@' in db_url else 'hidden'}")
    
    # Create database engine
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check sale table columns
            inspector = inspect(engine)
            sale_columns = [c['name'] for c in inspector.get_columns('sale')]
            
            print(f"\nCurrent sale table columns: {sale_columns}")
            
            # Check if total_amount exists
            if 'total_amount' not in sale_columns:
                print("\nWARNING: total_amount column is MISSING from sale table")
                print("Adding total_amount column...")
                
                # Add column
                conn.execute(text("""
                    ALTER TABLE sale 
                    ADD COLUMN total_amount NUMERIC(12, 2) DEFAULT 0 NOT NULL
                """))
                conn.commit()
                
                print("SUCCESS: Added total_amount column to sale table")
            else:
                print("\nOK: total_amount column already exists in sale table")
            
            # Check again to confirm
            inspector = inspect(engine)
            sale_columns_after = [c['name'] for c in inspector.get_columns('sale')]
            print(f"\nFinal sale table columns: {sale_columns_after}")
            
            if 'total_amount' in sale_columns_after:
                print("\nSUCCESS: Database schema is now correct!")
            else:
                print("\nERROR: Failed to add total_amount column")
                sys.exit(1)
                
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Production Database Schema Fix")
    print("=" * 60)
    fix_production_database()
    print("=" * 60)
