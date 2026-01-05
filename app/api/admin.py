"""
系统管理 API
"""
from flask import Blueprint, request, jsonify
from app.models import Spec, Customer, AuditLog
from app import db
from datetime import datetime

admin_api = Blueprint('admin_api', __name__)

# ==================== 规格管理 ====================

@admin_api.route('/specs', methods=['GET'])
def get_specs():
    """获取规格列表"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = Spec.query
        if active_only:
            query = query.filter(Spec.active == True)
        
        specs = query.order_by(Spec.name).all()
        return jsonify({'items': [spec.to_dict() for spec in specs]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api.route('/specs', methods=['POST'])
def create_spec():
    """创建规格"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'error': '规格名称不能为空'}), 400
        if not data.get('length'):
            return jsonify({'error': '长度不能为空'}), 400
        if not data.get('width'):
            return jsonify({'error': '宽度不能为空'}), 400
        if not data.get('kg_per_box'):
            return jsonify({'error': '单箱重量不能为空'}), 400
        
        # 检查名称是否已存在
        existing = Spec.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': '规格名称已存在'}), 400
        
        spec = Spec(
            name=data['name'],
            length=data['length'],
            width=data['width'],
            kg_per_box=data['kg_per_box'],
            created_by=data.get('created_by', 'system')
        )
        db.session.add(spec)
        db.session.commit()
        
        return jsonify(spec.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/specs/<int:spec_id>', methods=['PUT'])
def update_spec(spec_id):
    """更新规格"""
    try:
        spec = Spec.query.get(spec_id)
        if not spec:
            return jsonify({'error': '规格不存在'}), 404
        
        data = request.get_json()
        
        if 'kg_per_box' in data:
            spec.kg_per_box = data['kg_per_box']
        if 'updated_by' in data:
            spec.updated_by = data['updated_by']
        
        spec.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(spec.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/specs/<int:spec_id>/deactivate', methods=['POST'])
def deactivate_spec(spec_id):
    """禁用规格"""
    try:
        spec = Spec.query.get(spec_id)
        if not spec:
            return jsonify({'error': '规格不存在'}), 404
        
        data = request.get_json()
        spec.active = False
        spec.updated_by = data.get('updated_by', 'system')
        spec.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(spec.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 客户管理 ====================

@admin_api.route('/customers', methods=['GET'])
def get_customers():
    """获取客户列表"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = Customer.query
        if active_only:
            query = query.filter(Customer.active == True)
        
        customers = query.order_by(Customer.name).all()
        return jsonify({'items': [customer.to_dict() for customer in customers]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api.route('/customers', methods=['POST'])
def create_customer():
    """创建客户"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'error': '客户名称不能为空'}), 400
        
        # 检查名称是否已存在
        existing = Customer.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': '客户名称已存在'}), 400
        
        customer = Customer(
            name=data['name'],
            credit_allowed=data.get('credit_allowed', False),
            created_by=data.get('created_by', 'system')
        )
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """更新客户"""
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': '客户不存在'}), 404
        
        data = request.get_json()
        
        if 'credit_allowed' in data:
            customer.credit_allowed = data['credit_allowed']
        if 'updated_by' in data:
            customer.updated_by = data['updated_by']
        
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 审计日志 ====================

@admin_api.route('/audit-logs', methods=['GET'])
def get_audit_logs():
    """获取审计日志"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        table_name = request.args.get('table_name')
        record_id = request.args.get('record_id')
        action = request.args.get('action')
        
        query = AuditLog.query
        
        if table_name:
            query = query.filter(AuditLog.table_name == table_name)
        if record_id:
            query = query.filter(AuditLog.record_id == record_id)
        if action:
            query = query.filter(AuditLog.action == action)
        
        pagination = query.order_by(AuditLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'items': [log.to_dict() for log in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
