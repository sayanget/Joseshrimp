"""
直接测试生产环境的模板渲染
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Sale
from flask import render_template_string

app = create_app()

with app.app_context():
    print("=" * 60)
    print("Testing Template Rendering in Production")
    print("=" * 60)
    
    # 获取最新销售单
    sale = Sale.query.order_by(Sale.sale_time.desc()).first()
    
    if not sale:
        print("No sales found!")
        exit(1)
    
    print(f"\nSale ID: {sale.id}")
    print(f"total_kg: {sale.total_kg} (type: {type(sale.total_kg).__name__})")
    print()
    
    # 测试各种模板表达式
    test_templates = [
        ("Direct value", "{{ sale.total_kg }}"),
        ("With number filter", "{{ sale.total_kg|number(3) }}"),
        ("With default", "{{ sale.total_kg|default(0) }}"),
        ("With number(2)", "{{ sale.total_kg|number(2) }}"),
        ("Float conversion", "{{ sale.total_kg|float }}"),
        ("String conversion", "{{ sale.total_kg|string }}"),
    ]
    
    print("Template Rendering Tests:")
    print("-" * 60)
    
    for name, template in test_templates:
        try:
            result = render_template_string(template, sale=sale)
            print(f"{name:20} -> '{result}'")
        except Exception as e:
            print(f"{name:20} -> ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("Testing actual detail.html snippet:")
    
    # 测试实际模板片段
    actual_template = """
    <h1 class="display-4 text-success">
        {{ sale.total_kg|number(3) }}
    </h1>
    """
    
    rendered = render_template_string(actual_template, sale=sale)
    print(f"Rendered HTML:\n{rendered}")
    
    # 检查是否有空白或特殊字符
    import re
    numbers = re.findall(r'\d+\.?\d*', rendered)
    print(f"\nExtracted numbers: {numbers}")
