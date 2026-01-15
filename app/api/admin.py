"""
系统管理 API
"""
from flask import Blueprint, request, jsonify
from app.models import Spec, Customer, AuditLog, Product
from app import db
from datetime import datetime
from app.utils import timezone

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
        
        # Check if name is being changed and if it conflicts with existing spec
        if 'name' in data and data['name'] != spec.name:
            existing = Spec.query.filter_by(name=data['name']).first()
            if existing:
                return jsonify({'error': '规格名称已存在'}), 400
            spec.name = data['name']
        
        if 'kg_per_box' in data:
            spec.kg_per_box = data['kg_per_box']
        if 'updated_by' in data:
            spec.updated_by = data['updated_by']
        
        spec.updated_at = timezone.now()
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
        spec.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify(spec.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/specs/<int:spec_id>/activate', methods=['POST'])
def activate_spec(spec_id):
    """启用规格"""
    try:
        spec = Spec.query.get(spec_id)
        if not spec:
            return jsonify({'error': '规格不存在'}), 404
        
        data = request.get_json()
        spec.active = True
        spec.updated_by = data.get('updated_by', 'system')
        spec.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify(spec.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/specs/<int:spec_id>/prices', methods=['PUT'])
def update_spec_prices(spec_id):
    """更新规格价格"""
    try:
        spec = Spec.query.get(spec_id)
        if not spec:
            return jsonify({'error': '规格不存在'}), 404
        
        data = request.get_json()
        
        if 'cash_price' in data:
            spec.cash_price = data['cash_price']
        if 'credit_price' in data:
            spec.credit_price = data['credit_price']
        if 'updated_by' in data:
            spec.updated_by = data['updated_by']
        
        spec.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify(spec.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 系统设置 ====================

@admin_api.route('/settings/prices', methods=['PUT'])
def update_system_prices():
    """更新系统价格设置"""
    try:
        from app.models import SystemConfig
        data = request.get_json()
        
        updated_by = data.get('updated_by', 'admin')
        
        if 'price_cash' in data:
            SystemConfig.set_value(
                'price_cash',
                data['price_cash'],
                description='现金支付价格 ($/KG)',
                updated_by=updated_by
            )
        
        if 'price_credit' in data:
            SystemConfig.set_value(
                'price_credit',
                data['price_credit'],
                description='信用支付价格 ($/KG)',
                updated_by=updated_by
            )
        
        return jsonify({'message': 'Prices updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== 备忘录管理 ====================

@admin_api.route('/memos', methods=['GET'])
def get_memos():
    """获取备忘录列表"""
    try:
        from app.models import Memo
        date_str = request.args.get('date')
        
        query = Memo.query.filter_by(active=True)
        
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter(Memo.memo_date == target_date)
            except ValueError:
                # 如果日期格式错误，默认返回当天
                query = query.filter(Memo.memo_date == timezone.get_current_date())
        else:
            # 默认只显示今天的备忘录
            query = query.filter(Memo.memo_date == timezone.get_current_date())
            
        memos = query.order_by(Memo.created_at.desc()).all()
        return jsonify({'items': [memo.to_dict() for memo in memos]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api.route('/memos', methods=['POST'])
def create_memo():
    """创建备忘录"""
    try:
        from app.models import Memo
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'error': '内容不能为空'}), 400
            
        memo_date = timezone.get_current_date()
        if data.get('memo_date'):
            try:
                memo_date = datetime.strptime(data['memo_date'], '%Y-%m-%d').date()
            except ValueError:
                pass # Use default today if invalid
        
        memo = Memo(
            content=data['content'],
            memo_date=memo_date,
            reference_type=data.get('reference_type'),
            reference_id=data.get('reference_id'),
            created_by=data.get('created_by', 'admin')
        )
        db.session.add(memo)
        db.session.commit()
        
        return jsonify(memo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/memos/<int:memo_id>', methods=['PUT'])
def update_memo(memo_id):
    """更新备忘录"""
    try:
        from app.models import Memo
        memo = Memo.query.get(memo_id)
        if not memo:
            return jsonify({'error': '备忘录不存在'}), 404
            
        data = request.get_json()
        
        if 'content' in data:
            memo.content = data['content']
        if 'is_completed' in data:
            memo.is_completed = data['is_completed']
        if 'active' in data:
            memo.active = data['active']
        if 'updated_by' in data:
            memo.updated_by = data['updated_by']
            
        memo.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify(memo.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/memos/<int:memo_id>', methods=['DELETE'])
def delete_memo(memo_id):
    """删除备忘录（软删除）"""
    try:
        from app.models import Memo
        memo = Memo.query.get(memo_id)
        if not memo:
            return jsonify({'error': '备忘录不存在'}), 404
            
        memo.active = False
        memo.updated_by = request.args.get('updated_by', 'admin')
        memo.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify({'message': 'Memo deleted successfully'})
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
        
        customer.updated_at = timezone.now()
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

# ==================== 商品管理 ====================

@admin_api.route('/products', methods=['GET'])
def get_products():
    """获取商品列表"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = Product.query
        if active_only:
            query = query.filter(Product.active == True)
        
        products = query.order_by(Product.name).all()
        return jsonify({'items': [product.to_dict() for product in products]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api.route('/products', methods=['POST'])
def create_product():
    """创建商品"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({'error': '商品名称不能为空'}), 400
        if not data.get('cash_price'):
            return jsonify({'error': '现金价格不能为空'}), 400
        if not data.get('credit_price'):
            return jsonify({'error': '信用价格不能为空'}), 400
        
        # 验证价格为正数
        if float(data['cash_price']) <= 0:
            return jsonify({'error': '现金价格必须大于0'}), 400
        if float(data['credit_price']) <= 0:
            return jsonify({'error': '信用价格必须大于0'}), 400
        
        # 检查名称是否已存在
        existing = Product.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': '商品名称已存在'}), 400
        
        product = Product(
            name=data['name'],
            cash_price=data['cash_price'],
            credit_price=data['credit_price'],
            created_by=data.get('created_by', 'system')
        )
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新商品"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        
        data = request.get_json()
        
        # 检查名称是否被修改且与其他商品冲突
        if 'name' in data and data['name'] != product.name:
            existing = Product.query.filter_by(name=data['name']).first()
            if existing:
                return jsonify({'error': '商品名称已存在'}), 400
            product.name = data['name']
        
        # 更新价格
        if 'cash_price' in data:
            if float(data['cash_price']) <= 0:
                return jsonify({'error': '现金价格必须大于0'}), 400
            product.cash_price = data['cash_price']
        
        if 'credit_price' in data:
            if float(data['credit_price']) <= 0:
                return jsonify({'error': '信用价格必须大于0'}), 400
            product.credit_price = data['credit_price']
        
        if 'updated_by' in data:
            product.updated_by = data['updated_by']
        
        product.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/products/<int:product_id>/deactivate', methods=['POST'])
def deactivate_product(product_id):
    """禁用商品"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        
        data = request.get_json()
        product.active = False
        product.updated_by = data.get('updated_by', 'system')
        product.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api.route('/products/<int:product_id>/activate', methods=['POST'])
def activate_product(product_id):
    """启用商品"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        
        data = request.get_json()
        product.active = True
        product.updated_by = data.get('updated_by', 'system')
        product.updated_at = timezone.now()
        db.session.commit()
        
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
