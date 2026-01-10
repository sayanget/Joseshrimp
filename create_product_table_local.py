"""
为本地SQLite数据库创建product表
"""
from app import create_app, db
from app.models import Product
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    print("Current tables:", existing_tables)
    
    if 'product' not in existing_tables:
        print("\nCreating product table...")
        # 创建product表
        db.create_all()
        print("✓ Product table created successfully!")
    else:
        print("\n✓ Product table already exists")
    
    # 验证
    try:
        count = Product.query.count()
        print(f"✓ Product table is accessible with {count} products")
    except Exception as e:
        print(f"✗ Error accessing product table: {e}")
