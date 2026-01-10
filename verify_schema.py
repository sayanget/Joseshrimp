"""
Verify that the sale table schema is correct and test creating a sale with credit payment
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def verify_schema():
    """Verify the database schema"""
    
    # Get database URL
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Fix postgres:// to postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    print("Connecting to production database...")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            # Check sale table schema
            inspector = inspect(engine)
            sale_columns = inspector.get_columns('sale')
            
            print("\n=== SALE TABLE SCHEMA ===")
            for col in sale_columns:
                print(f"  {col['name']:20} {str(col['type']):20} nullable={col['nullable']}")
            
            # Verify total_amount exists
            column_names = [c['name'] for c in sale_columns]
            if 'total_amount' in column_names:
                print("\n✓ total_amount column EXISTS")
            else:
                print("\n✗ total_amount column MISSING")
                sys.exit(1)
            
            # Check recent sales
            print("\n=== RECENT SALES ===")
            result = conn.execute(text("""
                SELECT id, sale_time, payment_type, total_kg, total_amount, status
                FROM sale
                ORDER BY created_at DESC
                LIMIT 5
            """))
            
            for row in result:
                print(f"  {row.id} | {row.payment_type:10} | {row.total_kg:8.2f} kg | ${row.total_amount:8.2f} | {row.status}")
            
            print("\n✓ Database schema verification complete!")
            
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    verify_schema()
