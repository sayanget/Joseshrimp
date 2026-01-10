"""
Fix production database schema - Add missing unit_price field to sale_item table

This script adds the unit_price column that is missing from the sale_item table
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def fix_sale_item_schema():
    """Check and fix sale_item table schema"""
    
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
            # Check sale_item table columns
            inspector = inspect(engine)
            item_columns = [c['name'] for c in inspector.get_columns('sale_item')]
            
            print(f"\nCurrent sale_item table columns: {item_columns}")
            
            # Check if unit_price exists
            if 'unit_price' not in item_columns:
                print("\nWARNING: unit_price column is MISSING from sale_item table")
                print("Adding unit_price column...")
                
                # Add column
                conn.execute(text("""
                    ALTER TABLE sale_item 
                    ADD COLUMN unit_price NUMERIC(10, 2)
                """))
                conn.commit()
                
                print("SUCCESS: Added unit_price column to sale_item table")
            else:
                print("\nOK: unit_price column already exists in sale_item table")
            
            # Check if total_amount exists in sale_item
            if 'total_amount' not in item_columns:
                print("\nWARNING: total_amount column is MISSING from sale_item table")
                print("Adding total_amount column...")
                
                # Add column
                conn.execute(text("""
                    ALTER TABLE sale_item 
                    ADD COLUMN total_amount NUMERIC(12, 2) DEFAULT 0 NOT NULL
                """))
                conn.commit()
                
                print("SUCCESS: Added total_amount column to sale_item table")
            else:
                print("\nOK: total_amount column already exists in sale_item table")
            
            # Check again to confirm
            inspector = inspect(engine)
            item_columns_after = [c['name'] for c in inspector.get_columns('sale_item')]
            print(f"\nFinal sale_item table columns: {item_columns_after}")
            
            if 'unit_price' in item_columns_after and 'total_amount' in item_columns_after:
                print("\nSUCCESS: Database schema is now correct!")
            else:
                print("\nERROR: Failed to add required columns")
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
    print("Production Database Schema Fix - sale_item table")
    print("=" * 60)
    fix_sale_item_schema()
    print("=" * 60)
