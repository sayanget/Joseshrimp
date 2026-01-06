"""
系统管理视图
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Spec, Customer, AuditLog, User, Role, Permission
from app.utils.decorators import admin_required
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
@admin_required
def before_request():
    """Protect all admin routes"""
    pass

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

@admin_bp.route('/prices')
def manage_prices():
    """价格管理"""
    specs = Spec.query.order_by(Spec.name).all()
    return render_template('admin/prices.html', specs=specs)

@admin_bp.route('/settings')
def system_settings():
    """系统设置"""
    from app.models import SystemConfig
    configs = SystemConfig.query.all()
    return render_template('admin/settings.html', configs=configs)



@admin_bp.route('/audit')
def audit_logs():
    """审计日志"""
    page = request.args.get('page', 1, type=int)
    
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('admin/audit.html', pagination=pagination)

@admin_bp.route('/users')
def manage_users():
    """用户管理"""
    users = User.query.order_by(User.username).all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)

@admin_bp.route('/users/add', methods=['POST'])
def add_user():
    """添加用户"""
    username = request.form.get('username')
    password = request.form.get('password')
    role_id = request.form.get('role_id')
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('admin.manage_users'))
        
    user = User(username=username, role_id=role_id)
    user.password = password
    db.session.add(user)
    db.session.commit()
    
    flash('User created successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/edit/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    
    # Update password if provided
    password = request.form.get('password')
    if password:
        user.password = password
        
    # Update role
    role_id = request.form.get('role_id')
    if role_id:
        user.role_id = role_id
        
    # Update status
    active = request.form.get('active') == 'on'
    user.active = active
    
    db.session.commit()
    flash('User updated successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/roles')
def manage_roles():
    """角色管理"""
    roles = Role.query.all()
    permissions = Permission.query.all()
    return render_template('admin/roles.html', roles=roles, permissions=permissions)

@admin_bp.route('/roles/add', methods=['POST'])
def add_role():
    """添加角色"""
    name = request.form.get('name')
    permission_ids = request.form.getlist('permissions')
    
    if Role.query.filter_by(name=name).first():
        flash('Role name already exists.', 'danger')
        return redirect(url_for('admin.manage_roles'))
        
    role = Role(name=name)
    
    # Add permissions
    for perm_id in permission_ids:
        perm = Permission.query.get(perm_id)
        if perm:
            role.permissions.append(perm)
            
    db.session.add(role)
    db.session.commit()
    
    flash('Role created successfully.', 'success')
    return redirect(url_for('admin.manage_roles'))

@admin_bp.route('/roles/edit/<int:role_id>', methods=['POST'])
def edit_role(role_id):
    """编辑角色"""
    role = Role.query.get_or_404(role_id)
    
    # Update permissions
    permission_ids = request.form.getlist('permissions')
    
    # Clear existing permissions
    role.permissions = []
    
    # Add new permissions
    for perm_id in permission_ids:
        perm = Permission.query.get(perm_id)
        if perm:
            role.permissions.append(perm)
            
    db.session.commit()
    flash('Role updated successfully.', 'success')
    return redirect(url_for('admin.manage_roles'))

