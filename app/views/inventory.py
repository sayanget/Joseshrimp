"""
库存管理视图
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.inventory_service import InventoryService
from app.services.purchase_service import PurchaseService
from app.models import InventoryCheck
from datetime import datetime
from app.utils.decorators import permission_required

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

@inventory_bp.route('/check', methods=['GET', 'POST'])
def inventory_check():
    """库存盘点页面"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            actual_kg = float(data.get('actual_kg'))
            notes = data.get('notes', '')
            
            InventoryService.process_inventory_check(
                actual_kg=actual_kg,
                notes=notes,
                created_by=current_user.username
            )
            
            flash('库存盘点已提交', 'success')
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 400
            
    stock = InventoryService.get_current_stock()
    return render_template('inventory/check.html', stock=stock)

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
