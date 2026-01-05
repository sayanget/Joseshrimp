"""
库存管理视图
"""
from flask import Blueprint, render_template, request
from app.services.inventory_service import InventoryService

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/current')
def current_stock():
    """当前库存页面"""
    stock = InventoryService.get_current_stock()
    return render_template('inventory/current.html', stock=stock)

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

@inventory_bp.route('/check')
def inventory_check():
    """库存盘点页面"""
    stock = InventoryService.get_current_stock()
    return render_template('inventory/check.html', stock=stock)
