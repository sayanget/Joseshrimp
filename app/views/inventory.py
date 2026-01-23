"""
库存管理视图
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.services.inventory_service import InventoryService
from app.services.purchase_service import PurchaseService
from app.models import InventoryCheck
from datetime import datetime
from app.utils.decorators import permission_required
from app.utils import timezone

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.before_request
@login_required
@permission_required('view_inventory')
def before_request():
    """Protect all inventory routes"""
    pass

@inventory_bp.route('/current')
def current_stock():
    """当前库存页面"""
    stock = InventoryService.get_current_stock()
    product_stock = InventoryService.get_stock_by_product()
    return render_template('inventory/current.html', stock=stock, product_stock=product_stock)

@inventory_bp.route('/moves')
def stock_moves():
    """库存变动列表"""
    page = request.args.get('page', 1, type=int)
    move_type = request.args.get('move_type')
    
    pagination = InventoryService.get_stock_moves(
        page=page,
        per_page=20,
        move_type=move_type
    )
    
    return render_template('inventory/moves.html',
                         pagination=pagination,
                         move_type=move_type)

@inventory_bp.route('/purchase/create')
def create_purchase():
    """采购入库页面"""
    return render_template('inventory/purchase_create.html')

@inventory_bp.route('/purchase')
def list_purchases():
    """采购单列表页面"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'active')
    
    pagination = PurchaseService.get_purchase_list(
        page=page,
        per_page=20,
        status=status
    )
    
    return render_template('inventory/purchase_list.html',
                         pagination=pagination,
                         status=status)

@inventory_bp.route('/purchase/<purchase_id>')
def view_purchase(purchase_id):
    """采购单详情页面"""
    try:
        purchase = PurchaseService.get_purchase_detail(purchase_id)
        return render_template('inventory/purchase_detail.html', purchase=purchase)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('inventory.list_purchases'))

@inventory_bp.route('/product/<product_name>/sales')
def product_sales(product_name):
    """查看商品的销售记录"""
    from app.models import Sale, SaleItem, Product
    from app.services.sale_service import SaleService
    
    page = request.args.get('page', 1, type=int)
    
    # 查找商品
    product = Product.query.filter_by(name=product_name).first()
    if not product:
        flash(f'商品"{product_name}"不存在', 'error')
        return redirect(url_for('inventory.current_stock'))
    
    # 查询包含该商品的销售单
    pagination = db.session.query(Sale).join(
        SaleItem, Sale.id == SaleItem.sale_id
    ).filter(
        SaleItem.product_id == product.id,
        Sale.status == 'active'
    ).order_by(
        Sale.sale_time.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('inventory/product_sales.html', 
                         product=product,
                         pagination=pagination)

@inventory_bp.route('/purchase/export')
def export_purchases():
    """导出采购单列表为Excel"""
    from app.utils.excel_exporter import export_purchases_to_excel
    
    # 获取所有采购单
    purchases = Purchase.query.filter_by(status='active').order_by(Purchase.purchase_time.desc()).all()
    
    return export_purchases_to_excel(purchases)

    return export_purchases_to_excel(purchases)
