from app import create_app, db
from app.services.sale_service import SaleService
from app.models import Customer, Spec, Product, Sale
from decimal import Decimal

app = create_app()

with app.app_context():
    # Setup test data
    customer = Customer.query.first()
    spec = Spec.query.first()
    product = Product.query.first()
    
    if not customer or not spec or not product:
        print("Error: Missing test data (Customer, Spec, or Product)")
        exit(1)

    print(f"Using Customer: {customer.name}, Spec: {spec.name}, Product: {product.name}")

    # Test 1: Sale with Discount
    print("\n--- Test 1: Sale with Discount ---")
    items = [{
        'spec_id': spec.id,
        'product_id': product.id,
        'box_qty': 10,
        'extra_kg': 0
    }]
    # Calculate expected subtotal
    subtotal_kg = 10 * float(spec.kg_per_box)
    expected_subtotal = subtotal_kg * float(product.cash_price)
    discount = 10.0
    
    sale1 = SaleService.create_sale(
        customer_id=customer.id,
        payment_type='现金',
        items_data=items,
        created_by='TestScript',
        discount=discount
    )
    
    print(f"Sale ID: {sale1.id}")
    print(f"Subtotal Amount: {expected_subtotal}")
    print(f"Discount: {sale1.discount}")
    print(f"Total Amount: {sale1.total_amount}")
    
    if abs(float(sale1.total_amount) - (expected_subtotal - discount)) < 0.01:
        print("PASS: Discount logic correct")
    else:
        print("FAIL: Discount logic incorrect")

    # Test 2: Sale with Manual Total
    print("\n--- Test 2: Sale with Manual Total ---")
    manual_total = 500.00
    sale2 = SaleService.create_sale(
        customer_id=customer.id,
        payment_type='现金',
        items_data=items,
        created_by='TestScript',
        manual_total_amount=manual_total
    )
    
    print(f"Sale ID: {sale2.id}")
    print(f"Manual Total: {sale2.manual_total_amount}")
    print(f"Total Amount: {sale2.total_amount}")
    
    if abs(float(sale2.total_amount) - manual_total) < 0.01:
        print("PASS: Manual total logic correct")
    else:
        print("FAIL: Manual total logic incorrect")
        
    # Test 3: Standard Sale (No extra fields)
    print("\n--- Test 3: Standard Sale ---")
    sale3 = SaleService.create_sale(
        customer_id=customer.id,
        payment_type='现金',
        items_data=items,
        created_by='TestScript'
    )
    print(f"Sale ID: {sale3.id}")
    print(f"Total Amount: {sale3.total_amount}")
    
    if abs(float(sale3.total_amount) - expected_subtotal) < 0.01:
        print("PASS: Standard logic correct")
    else:
        print("FAIL: Standard logic incorrect")
