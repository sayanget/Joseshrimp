"""
测试number过滤器是否能正确处理Decimal
"""
from decimal import Decimal
from app import create_app

app = create_app()

with app.app_context():
    # 获取number过滤器
    number_filter = app.jinja_env.filters['number']
    
    print("Testing number filter with Decimal values:")
    print("=" * 60)
    
    # 测试各种值
    test_values = [
        Decimal('200.000'),
        Decimal('0.000'),
        Decimal('41.500'),
        None,
        '',
        0,
        200.0
    ]
    
    for value in test_values:
        try:
            result = number_filter(value, 3)
            print(f"Input: {repr(value):25} -> Output: '{result}'")
        except Exception as e:
            print(f"Input: {repr(value):25} -> ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Testing with actual Sale object:")
    
    from app.models import Sale
    sale = Sale.query.order_by(Sale.sale_time.desc()).first()
    
    if sale:
        print(f"Sale ID: {sale.id}")
        print(f"sale.total_kg type: {type(sale.total_kg)}")
        print(f"sale.total_kg value: {repr(sale.total_kg)}")
        print(f"sale.total_kg is None: {sale.total_kg is None}")
        print(f"sale.total_kg == 0: {sale.total_kg == 0}")
        
        # 测试过滤器
        result = number_filter(sale.total_kg, 3)
        print(f"number_filter result: '{result}'")
        
        # 测试模板渲染
        from flask import render_template_string
        template = "{{ value|number(3) }}"
        rendered = render_template_string(template, value=sale.total_kg)
        print(f"Template rendered: '{rendered}'")
