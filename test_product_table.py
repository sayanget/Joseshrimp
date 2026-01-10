"""测试Product表是否存在"""
from app import create_app, db
from app.models import Product

app = create_app()

with app.app_context():
    try:
        count = Product.query.count()
        print(f"✓ Product table exists with {count} products")
    except Exception as e:
        print(f"✗ Error: {e}")
