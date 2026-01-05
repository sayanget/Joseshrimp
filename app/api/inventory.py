"""
库存管理 API
"""
from flask import Blueprint, request, jsonify
from app.services.inventory_service import InventoryService
from app import db
from datetime import datetime

inventory_api = Blueprint('inventory_api', __name__)

@inventory_api.route('/current', methods=['GET'])
def get_current_stock():
    """获取当前库存"""
    try:
        stock = InventoryService.get_current_stock()
        return jsonify(stock)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/moves', methods=['GET'])
def get_stock_moves():
    """获取库存变动列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        move_type = request.args.get('move_type')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status = request.args.get('status', 'active')
        
        # 转换日期
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        
        pagination = InventoryService.get_stock_moves(
            page=page,
            per_page=per_page,
            move_type=move_type,
            date_from=date_from,
            date_to=date_to,
            status=status
        )
        
        return jsonify({
            'items': [move.to_dict() for move in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/moves', methods=['POST'])
def add_stock_move():
    """添加库存变动"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('move_type'):
            return jsonify({'error': '变动类型不能为空'}), 400
        if not data.get('source'):
            return jsonify({'error': '来源/去向不能为空'}), 400
        if data.get('kg') is None:
            return jsonify({'error': '重量不能为空'}), 400
        
        move = InventoryService.add_stock_move(
            move_type=data['move_type'],
            source=data['source'],
            kg=data['kg'],
            notes=data.get('notes'),
            created_by=data.get('created_by', 'system')
        )
        
        return jsonify(move.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/history', methods=['GET'])
def get_stock_history():
    """获取库存历史趋势"""
    try:
        days = request.args.get('days', 30, type=int)
        history = InventoryService.get_stock_history(days=days)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_api.route('/by-type', methods=['GET'])
def get_stock_by_type():
    """按类型统计库存变动"""
    try:
        stats = InventoryService.get_stock_by_type()
        return jsonify({'data': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
