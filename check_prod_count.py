import os
from app import create_app, db
from app.models import Sale, Customer, Spec

def check_counts():
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        os.environ['DATABASE_URL'] = db_url.replace("postgres://", "postgresql://", 1)

    app = create_app('production')
    with app.app_context():
        print(f"Specs: {Spec.query.count()}")
        print(f"Customers: {Customer.query.count()}")
        print(f"Sales: {Sale.query.count()}")

if __name__ == "__main__":
    check_counts()
