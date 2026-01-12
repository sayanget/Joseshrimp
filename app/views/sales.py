"""
销售管理视图
"""
from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required
from app.services.sale_service import SaleService
from app.models import Customer, Spec, Product
from datetime import datetime

from app.utils.decorators import permission_required

sales_bp = Blueprint('sales', __name__)

@sales_bp.before_request
@login_required
@permission_required('view_sales')
def before_request():
    """Protect all sales routes"""
    pass

@sales_bp.route('/')
def list_sales():
    """销售单列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'active')
    
    pagination = SaleService.get_sales_list(page=page, per_page=20, status=status)
    
    return render_template('sales/list.html',
                         pagination=pagination,
                         status=status)

@sales_bp.route('/create')
def create_sale():
    """创建销售单页面"""
    customers = Customer.query.filter_by(active=True).order_by(Customer.name).all()
    specs = Spec.query.filter_by(active=True).order_by(Spec.name).all()
    products = Product.query.filter_by(active=True).order_by(Product.name).all()
    
    return render_template('sales/create.html',
                         customers=customers,
                         specs=specs,
                         products=products)

@sales_bp.route('/<sale_id>')
def view_sale(sale_id):
    """查看销售单详情"""
    try:
        sale = SaleService.get_sale_detail(sale_id)
        return render_template('sales/detail.html', sale=sale)
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('sales.list_sales'))

@sales_bp.route('/daily/<date>')
def daily_sales(date):
    """查看指定日期的所有销售记录"""
    from flask import redirect, url_for
    
    try:
        # 验证日期格式
        sale_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # 获取当天的所有销售记录和汇总统计
        sales, summary = SaleService.get_sales_by_date(sale_date)
        
        return render_template('sales/daily_detail.html',
                             sales=sales,
                             summary=summary,
                             date=sale_date)
    except ValueError as e:
        flash('Invalid date format', 'error')
        return redirect(url_for('reports.daily_sales'))
    except Exception as e:
        flash(f'Error loading sales data: {str(e)}', 'error')
        return redirect(url_for('reports.daily_sales'))


@sales_bp.route('/payment-details')
def payment_details():
    """收款明细页面"""
    from app.models import Sale
    from sqlalchemy import func
    
    payment_type = request.args.get('payment_type')
    payment_status = request.args.get('payment_status')
    page = request.args.get('page', 1, type=int)
    
    today = datetime.now().date()
    query = Sale.query.filter(
        func.date(Sale.sale_time) == today,
        Sale.status == 'active'
    )
    
    if payment_type:
        query = query.filter(Sale.payment_type == payment_type)
    if payment_status:
        query = query.filter(Sale.payment_status == payment_status)
    
    pagination = query.order_by(Sale.sale_time.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # 计算总计
    total_amount = sum(float(s.total_amount) for s in pagination.items)
    total_kg = sum(float(s.total_kg) for s in pagination.items)
    
    return render_template('sales/payment_details.html',
                         pagination=pagination,
                         payment_type=payment_type,
                         payment_status=payment_status,
                         total_amount=total_amount,
                         total_kg=total_kg)


@sales_bp.route('/remittance')
def remittance_page():
    """回款页面"""
    from app.services.remittance_service import RemittanceService
    
    page = request.args.get('page', 1, type=int)
    payment_status = request.args.get('payment_status')
    
    # 获取信用结算记录列表
    pagination = RemittanceService.get_credit_sales_list(
        page=page,
        per_page=20,
        payment_status=payment_status
    )
    
    # 计算总计
    total_amount = sum(float(s.total_amount) for s in pagination.items)
    total_unpaid = sum(s.unpaid_amount for s in pagination.items)
    total_paid = sum(s.paid_amount for s in pagination.items)
    
    return render_template('sales/remittance.html',
                         pagination=pagination,
                         payment_status=payment_status,
                         total_amount=total_amount,
                         total_unpaid=total_unpaid,
                         total_paid=total_paid)

