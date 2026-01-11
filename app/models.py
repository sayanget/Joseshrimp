"""
数据库模型定义
"""
from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint, event
from sqlalchemy.orm import validates
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class SystemConfig(db.Model):
    """系统配置表"""
    __tablename__ = 'system_config'
    
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    
    @staticmethod
    def get_value(key, default=None, value_type=str):
        """获取配置值"""
        config = SystemConfig.query.get(key)
        if not config:
            return default
        
        try:
            if value_type == float:
                return float(config.value)
            elif value_type == int:
                return int(config.value)
            elif value_type == bool:
                return config.value.lower() in ('true', '1', 'yes')
            else:
                return config.value
        except:
            return default
    
    @staticmethod
    def set_value(key, value, description=None, updated_by=None):
        """设置配置值"""
        config = SystemConfig.query.get(key)
        if config:
            config.value = str(value)
            if description:
                config.description = description
            if updated_by:
                config.updated_by = updated_by
            config.updated_at = datetime.utcnow()
        else:
            config = SystemConfig(
                key=key,
                value=str(value),
                description=description,
                updated_by=updated_by
            )
            db.session.add(config)
        db.session.commit()
        return config
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }


class Spec(db.Model):
    """规格表"""
    __tablename__ = 'spec'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    kg_per_box = db.Column(db.Numeric(10, 3), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    
    # 关系
    sale_items = db.relationship('SaleItem', backref='spec', lazy='dynamic')
    
    __table_args__ = (
        CheckConstraint('kg_per_box > 0', name='check_kg_per_box_positive'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'length': self.length,
            'width': self.width,
            'kg_per_box': float(self.kg_per_box),
            'active': self.active
        }
    
    def __repr__(self):
        return f'<Spec {self.name}>'


class Customer(db.Model):
    """客户表"""
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    credit_allowed = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    
    # 关系
    sales = db.relationship('Sale', backref='customer', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'credit_allowed': self.credit_allowed,
            'active': self.active
        }
    
    def __repr__(self):
        return f'<Customer {self.name}>'


class Product(db.Model):
    """商品表"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    cash_price = db.Column(db.Numeric(10, 2), nullable=False)  # 现金结算价格($/KG)
    credit_price = db.Column(db.Numeric(10, 2), nullable=False)  # 信用结算价格($/KG)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    
    # 关系
    sale_items = db.relationship('SaleItem', backref='product', lazy='dynamic')
    
    __table_args__ = (
        CheckConstraint('cash_price > 0', name='check_cash_price_positive'),
        CheckConstraint('credit_price > 0', name='check_credit_price_positive'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cash_price': float(self.cash_price),
            'credit_price': float(self.credit_price),
            'active': self.active
        }
    
    def __repr__(self):
        return f'<Product {self.name}>'


class Purchase(db.Model):
    """采购单主表"""
    __tablename__ = 'purchase'
    
    id = db.Column(db.String(50), primary_key=True)
    purchase_time = db.Column(db.DateTime, nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    total_kg = db.Column(db.Numeric(12, 3), default=0, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)
    payment_status = db.Column(db.String(20), default='unpaid', nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)
    void_reason = db.Column(db.Text)
    void_time = db.Column(db.DateTime)
    void_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    
    # 关系
    items = db.relationship('PurchaseItem', backref='purchase', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint("payment_status IN ('unpaid','partial','paid')", 
                       name='check_payment_status'),
        CheckConstraint("status IN ('active','void')", 
                       name='check_purchase_status'),
    )
    
    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'purchase_time': self.purchase_time.isoformat() if self.purchase_time else None,
            'supplier': self.supplier,
            'total_kg': float(self.total_kg),
            'total_amount': float(self.total_amount),
            'payment_status': self.payment_status,
            'notes': self.notes,
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if self.status == 'void':
            data['void_reason'] = self.void_reason
            data['void_time'] = self.void_time.isoformat() if self.void_time else None
            data['void_by'] = self.void_by
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data
    
    def __repr__(self):
        return f'<Purchase {self.id}>'


class PurchaseItem(db.Model):
    """采购明细表"""
    __tablename__ = 'purchase_item'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.String(50), db.ForeignKey('purchase.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    kg = db.Column(db.Numeric(10, 3), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('kg > 0', name='check_purchase_kg_positive'),
        CheckConstraint('unit_price > 0', name='check_purchase_unit_price_positive'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'kg': float(self.kg),
            'unit_price': float(self.unit_price),
            'total_amount': float(self.total_amount)
        }
    
    def __repr__(self):
        return f'<PurchaseItem {self.id} for Purchase {self.purchase_id}>'


class Sale(db.Model):
    """销售单主表"""
    __tablename__ = 'sale'
    
    id = db.Column(db.String(50), primary_key=True)
    sale_time = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    total_kg = db.Column(db.Numeric(12, 3), default=0, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)  # 总金额
    payment_status = db.Column(db.String(20), default='unpaid', nullable=False)  # 收款状态：unpaid/partial/paid
    status = db.Column(db.String(20), default='active', nullable=False)
    void_reason = db.Column(db.Text)
    void_time = db.Column(db.DateTime)
    void_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(50))
    
    # 关系
    items = db.relationship('SaleItem', backref='sale', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    __table_args__ = (
        CheckConstraint("payment_type IN ('现金','Crédito')", 
                       name='check_payment_type'),
        CheckConstraint("payment_status IN ('unpaid','partial','paid')",
                       name='check_payment_status'),
        CheckConstraint("status IN ('active','void')", 
                       name='check_status'),
    )
    
    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'sale_time': self.sale_time.isoformat() if self.sale_time else None,
            'customer': self.customer.to_dict() if self.customer else None,
            'payment_type': self.payment_type,
            'payment_status': self.payment_status,
            'total_kg': float(self.total_kg),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if self.status == 'void':
            data['void_reason'] = self.void_reason
            data['void_time'] = self.void_time.isoformat() if self.void_time else None
            data['void_by'] = self.void_by
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data
    
    def __repr__(self):
        return f'<Sale {self.id}>'


class SaleItem(db.Model):
    """销售明细表"""
    __tablename__ = 'sale_item'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.String(50), db.ForeignKey('sale.id'), nullable=False)
    spec_id = db.Column(db.Integer, db.ForeignKey('spec.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)  # 商品ID(可选)
    box_qty = db.Column(db.Integer, default=0, nullable=False)
    extra_kg = db.Column(db.Numeric(10, 3), default=0, nullable=False)
    subtotal_kg = db.Column(db.Numeric(12, 3), default=0, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=True)  # 单价（每KG）
    total_amount = db.Column(db.Numeric(12, 2), default=0, nullable=False)  # 小计金额
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('box_qty >= 0', name='check_box_qty_non_negative'),
        CheckConstraint('extra_kg >= 0', name='check_extra_kg_non_negative'),
    )
    
    def calculate_subtotal(self):
        """计算小计重量"""
        if self.spec:
            self.subtotal_kg = self.box_qty * self.spec.kg_per_box + self.extra_kg
    
    def to_dict(self):
        return {
            'id': self.id,
            'spec': self.spec.to_dict() if self.spec else None,
            'product': self.product.to_dict() if self.product else None,
            'box_qty': self.box_qty,
            'extra_kg': float(self.extra_kg),
            'subtotal_kg': float(self.subtotal_kg),
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_amount': float(self.total_amount)
        }
    
    def __repr__(self):
        return f'<SaleItem {self.id} for Sale {self.sale_id}>'


class StockMove(db.Model):
    """库存变动表"""
    __tablename__ = 'stock_move'
    
    id = db.Column(db.Integer, primary_key=True)
    move_type = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    kg = db.Column(db.Numeric(12, 3), nullable=False)
    move_time = db.Column(db.DateTime, nullable=False)
    reference_id = db.Column(db.String(50))
    reference_type = db.Column(db.String(20))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)
    void_reason = db.Column(db.Text)
    void_time = db.Column(db.DateTime)
    void_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    
    __table_args__ = (
        CheckConstraint("move_type IN ('进货','调拨','退货','盘盈','盘亏','销售')", 
                       name='check_move_type'),
        CheckConstraint("status IN ('active','void')", 
                       name='check_stock_status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'move_type': self.move_type,
            'source': self.source,
            'kg': float(self.kg),
            'move_time': self.move_time.isoformat() if self.move_time else None,
            'reference_id': self.reference_id,
            'reference_type': self.reference_type,
            'status': self.status,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<StockMove {self.id} {self.move_type}>'


class AuditLog(db.Model):
    """审计日志表"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50))
    
    __table_args__ = (
        CheckConstraint("action IN ('INSERT','UPDATE','DELETE','VOID')", 
                       name='check_action'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<AuditLog {self.id} {self.table_name}.{self.record_id}>'


class InventoryCheck(db.Model):
    """盘点记录表"""
    __tablename__ = 'inventory_check'
    
    id = db.Column(db.Integer, primary_key=True)
    check_time = db.Column(db.DateTime, nullable=False)
    actual_kg = db.Column(db.Numeric(12, 3), nullable=False)
    theoretical_kg = db.Column(db.Numeric(12, 3), nullable=False)
    difference_kg = db.Column(db.Numeric(12, 3), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by = db.Column(db.String(50), nullable=False)
    
    def calculate_difference(self):
        """计算差异"""
        self.difference_kg = self.actual_kg - self.theoretical_kg
    
    def to_dict(self):
        return {
            'id': self.id,
            'check_time': self.check_time.isoformat() if self.check_time else None,
            'actual_kg': float(self.actual_kg),
            'theoretical_kg': float(self.theoretical_kg),
            'difference_kg': float(self.difference_kg),
            'notes': self.notes,
            'created_by': self.created_by
        }
    
    def __repr__(self):
        return f'<InventoryCheck {self.id}>'


# ==================== 权限管理模型 ====================

roles_permissions = db.Table('roles_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Permission(db.Model):
    """权限表"""
    __tablename__ = 'permission'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class Role(db.Model):
    """角色表"""
    __tablename__ = 'role'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.relationship('Permission', secondary=roles_permissions,
                                backref=db.backref('roles', lazy='dynamic'))
    
    def has_permission(self, perm_name):
        """检查角色是否有指定权限"""
        for perm in self.permissions:
            if perm.name == perm_name:
                return True
        return False
        
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255))  # Increased from 128 for bcrypt/scrypt compatibility
    active = db.Column(db.Boolean, default=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def can(self, perm_name):
        return self.role is not None and self.role.has_permission(perm_name)
    
    def is_admin(self):
        return self.can('admin')
        
    def __repr__(self):
        return f'<User {self.username}>'

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    
    def is_admin(self):
        return False




# ==================== SQLAlchemy事件监听器（模拟触发器） ====================

@event.listens_for(SaleItem, 'before_insert')
@event.listens_for(SaleItem, 'before_update')
def calculate_sale_item_subtotal(mapper, connection, target):
    """自动计算销售明细小计"""
    if target.spec_id:
        spec = db.session.query(Spec).get(target.spec_id)
        if spec:
            target.subtotal_kg = target.box_qty * spec.kg_per_box + target.extra_kg

# DISABLED: This event listener conflicts with manual total_kg calculation in create_sale()
# The manual calculation using database queries is more reliable and avoids
# SQLAlchemy attribute history warnings
#
# @event.listens_for(SaleItem, 'after_insert')
# @event.listens_for(SaleItem, 'after_update')
# @event.listens_for(SaleItem, 'after_delete')
# def update_sale_total(mapper, connection, target):
#     """自动更新销售单总重量"""
#     sale = db.session.query(Sale).get(target.sale_id)
#     if sale:
#         total = db.session.query(db.func.sum(SaleItem.subtotal_kg))\
#             .filter(SaleItem.sale_id == target.sale_id).scalar() or 0
#         sale.total_kg = total


@event.listens_for(Sale, 'after_insert')
def create_stock_move_on_sale(mapper, connection, target):
    """销售时自动创建库存变动记录"""
    if target.status == 'active' and target.total_kg > 0:
        customer = db.session.query(Customer).get(target.customer_id)
        stock_move = StockMove(
            move_type='销售',
            source=customer.name if customer else 'Unknown',
            kg=-target.total_kg,
            move_time=target.sale_time,
            reference_id=target.id,
            reference_type='sale',
            created_by=target.created_by
        )
        db.session.add(stock_move)


@event.listens_for(Sale, 'after_update')
def void_stock_move_on_sale_void(mapper, connection, target):
    """销售作废时更新库存变动"""
    # 检查状态是否从active变为void
    history = db.inspect(target).attrs.status.history
    if history.has_changes() and target.status == 'void':
        # 作废关联的库存变动
        stock_moves = db.session.query(StockMove)\
            .filter(StockMove.reference_type == 'sale')\
            .filter(StockMove.reference_id == target.id)\
            .all()
        for move in stock_moves:
            move.status = 'void'
            move.void_reason = target.void_reason
            move.void_time = target.void_time
            move.void_by = target.void_by


@event.listens_for(InventoryCheck, 'before_insert')
@event.listens_for(InventoryCheck, 'before_update')
def calculate_inventory_difference(mapper, connection, target):
    """自动计算盘点差异"""
    target.difference_kg = target.actual_kg - target.theoretical_kg
