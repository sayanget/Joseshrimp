"""
采购API路由
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.purchase_service import PurchaseService
from app.utils.decorators import permission_required

purchase_api = Blueprint('purchase_api', __name__)

@purchase_api.before_request
@login_required
@permission_required('create_purchase')
def before_request():
    """Protect all purchase API routes"""
    pass

@purchase_api.route('/', methods=['POST'])
def create_purchase():
    """创建采购单API"""
    try:
        data = request.get_json()
        
        supplier = data.get('supplier')
        items_data = data.get('items', [])
        notes = data.get('notes')
        
        if not supplier:
            return jsonify({'error': '供应商不能为空'}), 400
        
        if not items_data:
            return jsonify({'error': '采购明细不能为空'}), 400
        
        purchase = PurchaseService.create_purchase(
            supplier=supplier,
            items_data=items_data,
            created_by=current_user.username,
            notes=notes
        )
        
        return jsonify({
            'success': True,
            'purchase': purchase.to_dict(include_items=True)
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'创建采购单失败: {str(e)}'}), 500

@purchase_api.route('/', methods=['GET'])
def list_purchases():
    """采购单列表API"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', 'active')
        
        pagination = PurchaseService.get_purchase_list(
            page=page,
            per_page=per_page,
            status=status
        )
        
        return jsonify({
            'purchases': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
        
    except Exception as e:
        return jsonify({'error': f'获取采购单列表失败: {str(e)}'}), 500

@purchase_api.route('/<purchase_id>', methods=['GET'])
def get_purchase(purchase_id):
    """采购单详情API"""
    try:
        purchase = PurchaseService.get_purchase_detail(purchase_id)
        return jsonify(purchase.to_dict(include_items=True))
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'获取采购单详情失败: {str(e)}'}), 500
