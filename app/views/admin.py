"""
系统管理视图
"""
from flask import Blueprint, render_template, request
from app.models import Spec, Customer, AuditLog

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/specs')
def manage_specs():
    """规格管理"""
    specs = Spec.query.order_by(Spec.name).all()
    return render_template('admin/specs.html', specs=specs)

@admin_bp.route('/customers')
def manage_customers():
    """客户管理"""
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('admin/customers.html', customers=customers)

@admin_bp.route('/audit')
def audit_logs():
    """审计日志"""
    page = request.args.get('page', 1, type=int)
    
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/audit.html', pagination=pagination)
