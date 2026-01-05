"""
Flask应用入口文件
"""
import os
from app import create_app, db

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    """为Flask shell提供上下文"""
    from app.models import Spec, Customer, Sale, SaleItem, StockMove, AuditLog, InventoryCheck
    return {
        'db': db,
        'Spec': Spec,
        'Customer': Customer,
        'Sale': Sale,
        'SaleItem': SaleItem,
        'StockMove': StockMove,
        'AuditLog': AuditLog,
        'InventoryCheck': InventoryCheck
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
