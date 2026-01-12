"""
Production Database Migration Script
Adds discount and manual_total_amount columns to sale table
Compatible with PostgreSQL (Render production database)
"""
from app import create_app, db
from sqlalchemy import text

def migrate_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='sale' 
                AND column_name IN ('discount', 'manual_total_amount')
            """))
            existing_columns = [row[0] for row in result]
            
            # Add discount column if it doesn't exist
            if 'discount' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE sale 
                    ADD COLUMN discount NUMERIC(12, 2) DEFAULT 0
                """))
                print("✓ Added 'discount' column to sale table")
            else:
                print("- 'discount' column already exists")
            
            # Add manual_total_amount column if it doesn't exist
            if 'manual_total_amount' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE sale 
                    ADD COLUMN manual_total_amount NUMERIC(12, 2)
                """))
                print("✓ Added 'manual_total_amount' column to sale table")
            else:
                print("- 'manual_total_amount' column already exists")
            
            db.session.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate_database()
