"""
销售管理 API
"""
from flask import Blueprint, request, jsonify
from app.services.sale_service import SaleService
from app.services.remittance_service import RemittanceService
from app import db
from datetime import datetime

sales_api = Blueprint('sales_api', __name__)

@sales_api.route('', methods=['GET'])
def get_sales():
    """获取销售单列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # 转换日期
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        
        pagination = SaleService.get_sales_list(
            page=page,
            per_page=per_page,
            status=status,
            customer_id=customer_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return jsonify({
            'items': [sale.to_dict() for sale in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_api.route('/<sale_id>', methods=['GET'])
def get_sale(sale_id):
    """获取销售单详情"""
    try:
        sale = SaleService.get_sale_detail(sale_id)
        return jsonify(sale.to_dict(include_items=True))
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sales_api.route('', methods=['POST'])
def create_sale():
    """创建销售单"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('customer_id'):
            return jsonify({'error': '客户ID不能为空'}), 400
        if not data.get('payment_type'):
            return jsonify({'error': '支付方式不能为空'}), 400
        if not data.get('items') or len(data.get('items')) == 0:
            return jsonify({'error': '销售明细不能为空'}), 400
        
        sale = SaleService.create_sale(
            customer_id=data['customer_id'],
            payment_type=data['payment_type'],
            items_data=data['items'],
            discount=data.get('discount', 0),
            manual_total_amount=data.get('manual_total_amount'),
            created_by=data.get('created_by', 'system')
        )
        
        return jsonify(sale.to_dict(include_items=True)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_api.route('/<sale_id>/void', methods=['POST'])
def void_sale(sale_id):
    """作废销售单"""
    try:
        data = request.get_json()
        
        if not data.get('void_reason'):
            return jsonify({'error': '作废原因不能为空'}), 400
        
        sale = SaleService.void_sale(
            sale_id=sale_id,
            void_reason=data['void_reason'],
            void_by=data.get('void_by', 'system')
        )
        
        return jsonify(sale.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@sales_api.route('/today-summary', methods=['GET'])
def today_summary():
    """今日销售汇总"""
    try:
        summary = SaleService.get_today_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 回款管理 API ====================

@sales_api.route('/credit-sales', methods=['GET'])
def get_credit_sales():
    """获取信用结算记录列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        payment_status = request.args.get('payment_status')
        
        pagination = RemittanceService.get_credit_sales_list(
            page=page,
            per_page=per_page,
            payment_status=payment_status
        )
        
        # 转换为字典并添加回款信息
        items = []
        for sale in pagination.items:
            sale_dict = sale.to_dict()
            sale_dict['paid_amount'] = sale.paid_amount
            sale_dict['unpaid_amount'] = sale.unpaid_amount
            items.append(sale_dict)
        
        return jsonify({
            'items': items,
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sales_api.route('/remittance', methods=['POST'])
def create_remittance():
    """创建回款记录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('sale_id'):
            return jsonify({'error': '销售单号不能为空'}), 400
        if not data.get('amount'):
            return jsonify({'error': '回款金额不能为空'}), 400
        if not data.get('created_by'):
            return jsonify({'error': '创建人不能为空'}), 400
        
        # 解析回款时间
        remittance_time = None
        if data.get('remittance_time'):
            try:
                remittance_time = datetime.fromisoformat(data['remittance_time'])
            except:
                return jsonify({'error': '回款时间格式错误'}), 400
        
        remittance = RemittanceService.create_remittance(
            sale_id=data['sale_id'],
            amount=data['amount'],
            created_by=data['created_by'],
            notes=data.get('notes'),
            remittance_time=remittance_time
        )
        
        return jsonify(remittance.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sales_api.route('/remittance/<sale_id>', methods=['GET'])
def get_remittance_history(sale_id):
    """获取回款历史"""
    try:
        history = RemittanceService.get_remittance_history(sale_id)
        summary = RemittanceService.get_remittance_summary(sale_id)
        
        return jsonify({
            'history': history,
            'summary': summary
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
