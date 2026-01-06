from app import create_app, db
from app.models import Sale, SaleItem, StockMove, InventoryCheck, Customer, Spec, User, Role, Permission
from datetime import datetime
import uuid

app = create_app()

def reset_db():
    print("Resetting database (clearing transaction data)...")
    # Clear transaction tables
    SaleItem.query.delete()
    Sale.query.delete()
    StockMove.query.delete()
    InventoryCheck.query.delete()
    Customer.query.delete()
    Spec.query.delete()
    db.session.commit()
    print("Database cleared.")

def import_data():
    print("Importing data from table01.jpg...")
    
    # Create Specs (Assuming ~40kg box weight if not specified)
    specs_data = [
        "39X110", "38X104", "38X110", "38X115", "39X115", 
        "39X105", "40X115", "40X120", "38X120"
    ]
    
    specs = {}
    for code in specs_data:
        # Try to parse dimensions
        try:
            parts = code.split('X')
            if len(parts) != 2:
                parts = code.split('x')
            
            width = float(parts[0])
            length = float(parts[1])
            kg_per_box = 40.0 # Default based on image (2 javas = 80kg often implied)
            
            spec = Spec(name=code, width=width, length=length, kg_per_box=kg_per_box, created_by='admin')
            db.session.add(spec)
            specs[code] = spec
        except Exception as e:
            print(f"Error parsing spec {code}: {e}")
            raise e
            
    # Create General Spec for KG-only items
    # Constraint kg_per_box > 0 requires a positive value. We use 1.0 but box_qty will be 0.
    general_spec = Spec(name="GENERAL", width=0, length=0, kg_per_box=1.0, created_by='admin')
    db.session.add(general_spec)
    specs["GENERAL"] = general_spec
    
    print("Specs loaded:", list(specs.keys()))
            
    db.session.commit()
    
    # Create Customers
    customers_data = [
        "DANIEL HIELO", "doña lety", "CARLOS YESSENIA", "sujeli juarez", 
        "hermano ramon", "lizardo burgueno", "david", "Chaya juarez", 
        "fernanda 2", "laurita cerdan", "nina mercado", "paloma maz", 
        "Rosario cerdan", "Karla", "Ana fer", "linda juarez", 
        "Cipriano", "marlen cerdan", "guero reynosa", "diego cubetero"
    ]
    
    customers = {}
    for name in customers_data:
        customer = Customer(name=name, created_by='admin', credit_allowed=True)
        db.session.add(customer)
        customers[name] = customer
        
    db.session.commit()
    
    # Get admin user for creation logs
    admin_user = User.query.filter_by(username='admin').first()
    user_name = admin_user.username if admin_user else 'system'

    # Transactions Data
    transactions = [
        # 14/12/2025
        {"date": "2025-12-14", "customer": "DANIEL HIELO", "items": [{"kg": 20, "price": 110}], "payment": "credit"},
        {"date": "2025-12-14", "customer": "doña lety", "items": [{"spec": "39X110", "boxes": 2}], "payment": "credit"},
        {"date": "2025-12-14", "customer": "CARLOS YESSENIA", "items": [{"kg": 20, "price": 110}], "payment": "credit"},
        {"date": "2025-12-14", "customer": "sujeli juarez", "items": [{"spec": "39X110", "boxes": 1}], "payment": "credit"},
        
        # 13/12/2025
        {"date": "2025-12-13", "customer": "hermano ramon", "items": [{"spec": "38X104", "boxes": 2}, {"kg": 30, "price": 104}], "payment": "credit"},
        {"date": "2025-12-13", "customer": "lizardo burgueno", "items": [{"spec": "39X110", "boxes": 3}, {"spec": "38X115", "boxes": 2}], "payment": "credit"},
        {"date": "2025-12-13", "customer": "hermano ramon", "items": [{"spec": "38X104", "boxes": 6}, {"spec": "38X110", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-13", "customer": "david", "items": [{"spec": "38X115", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-13", "customer": "DANIEL HIELO", "items": [{"spec": "39X110", "boxes": 5}], "payment": "credit"},
        {"date": "2025-12-13", "customer": "DANIEL HIELO", "items": [{"kg": 25, "price": 115}], "payment": "credit"},
        {"date": "2025-12-13", "customer": "Chaya juarez", "items": [{"spec": "39X110", "boxes": 1, "extra_kg": 3}], "payment": "credit"}, # 43kg implies 3kg extra
        {"date": "2025-12-13", "customer": "fernanda 2", "items": [{"spec": "39X110", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-13", "customer": "laurita cerdan", "items": [{"spec": "40X115", "boxes": 1}], "payment": "credit"},
        
        # 12/12/2025
        {"date": "2025-12-12", "customer": "hermano ramon", "items": [{"spec": "38X104", "boxes": 2}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "DANIEL HIELO", "items": [{"kg": 15, "price": 110}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "nina mercado", "items": [{"spec": "39X115", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "paloma maz", "items": [{"spec": "39X115", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "lizardo burgueno", "items": [{"spec": "39X110", "boxes": 1, "extra_kg": 42}], "payment": "credit"}, # 28kg + 14kg extra = 42
        {"date": "2025-12-12", "customer": "Rosario cerdan", "items": [{"spec": "39X110", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "Karla", "items": [{"spec": "39X115", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "Ana fer", "items": [{"spec": "39X110", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "linda juarez", "items": [{"spec": "39X110", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "fernanda 2", "items": [{"spec": "39X110", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "sujeli juarez", "items": [{"spec": "39X110", "boxes": 1}, {"spec": "39X105", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "Cipriano", "items": [{"spec": "39X105", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-12", "customer": "Chaya juarez", "items": [{"spec": "39X110", "boxes": 1}], "payment": "credit"},
        
        # 11/12/2025
        {"date": "2025-12-11", "customer": "DANIEL HIELO", "items": [{"kg": 10, "price": 115}], "payment": "credit"},
        {"date": "2025-12-11", "customer": "david", "items": [{"spec": "38X115", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-11", "customer": "doña lety", "items": [{"spec": "39X115", "boxes": 2}], "payment": "credit"},
        {"date": "2025-12-11", "customer": "marlen cerdan", "items": [{"kg": 20, "price": 115}], "payment": "credit"},
        {"date": "2025-12-11", "customer": "hermano ramon", "items": [{"spec": "38X110", "boxes": 1}, {"spec": "38X120", "boxes": 3}, {"spec": "38X104", "boxes": 4}], "payment": "credit"},
        {"date": "2025-12-11", "customer": "guero reynosa", "items": [{"spec": "40X120", "boxes": 1}], "payment": "credit"},
        {"date": "2025-12-11", "customer": "diego cubetero", "items": [{"spec": "39X105", "boxes": 2}], "payment": "credit"},
    ]
    
    count = 0
    for t_data in transactions:
        customer = customers.get(t_data["customer"])
        if not customer:
            print(f"Customer not found: {t_data['customer']}")
            continue
            
        sale_id = uuid.uuid4().hex[:8].upper()
        sale_payment = "Crédito" if t_data["payment"] == "credit" else "现金"
        sale_time = datetime.strptime(t_data["date"] + " 10:00:00", "%Y-%m-%d %H:%M:%S")
        
        sale = Sale(
            id=sale_id,
            customer_id=customer.id,
            payment_type=sale_payment,
            sale_time=sale_time,
            created_at=sale_time,
            created_by=user_name,
            total_kg=0 # Will update below
        )
        db.session.add(sale)
        db.session.flush() 
        
        total_kg = 0
        for item_data in t_data["items"]:
            item = SaleItem(sale_id=sale.id)
            
            if "spec" in item_data:
                spec = specs.get(item_data["spec"])
                item.spec_id = spec.id
                item.box_qty = item_data["boxes"]
                item.extra_kg = item_data.get("extra_kg", 0)
                item.subtotal_kg = (float(spec.kg_per_box) * item.box_qty) + item.extra_kg
            else:
                # Extra KG Only items
                item.spec_id = specs["GENERAL"].id
                item.box_qty = 0
                item.extra_kg = item_data["kg"]
                item.subtotal_kg = item_data["kg"]
            
            total_kg += float(item.subtotal_kg)
            db.session.add(item)
            
        sale.total_kg = total_kg
        count += 1
        
    db.session.commit()
    print(f"Imported {count} transactions successfully.")

if __name__ == "__main__":
    with app.app_context():
        reset_db()
        import_data()
