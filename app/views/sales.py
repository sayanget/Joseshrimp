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
        
        # 获取当天的所有销售记录
        sales = SaleService.get_sales_by_date(sale_date)
        
        return render_template('sales/daily_detail.html',
                             sales=sales,
                             date=sale_date)
    except ValueError as e:
        flash('Invalid date format', 'error')
        return redirect(url_for('reports.daily_sales'))
    except Exception as e:
        flash(f'Error loading sales data: {str(e)}', 'error')
        return redirect(url_for('reports.daily_sales'))



