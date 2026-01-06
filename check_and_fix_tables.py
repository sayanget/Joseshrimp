import os
from app import create_app, db
from sqlalchemy import inspect

def check_and_fix():
    print("Checking tables...")
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Existing tables: {tables}")
        
        print("Running db.create_all()...")
        db.create_all()
        print("Done.")
        
        tables_after = inspector.get_table_names()
        print(f"Tables after create_all: {tables_after}")

if __name__ == "__main__":
    check_and_fix()
