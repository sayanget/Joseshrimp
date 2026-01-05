# Web 应用架构设计

## 一、系统架构概览

### 1.1 整体架构

```mermaid
graph TB
    subgraph 客户端层
        A[Web浏览器]
        B[移动浏览器]
    end
    
    subgraph 前端层
        C[HTML/CSS/JavaScript]
        D[Bootstrap UI]
        E[Chart.js 图表]
    end
    
    subgraph 后端层
        F[Flask Web框架]
        G[RESTful API]
        H[业务逻辑层]
        I[数据访问层]
    end
    
    subgraph 数据层
        J[SQLite数据库]
        K[文件存储]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    D --> G
    E --> G
    G --> H
    H --> I
    I --> J
    I --> K
```

### 1.2 技术栈选择

| 层级 | 技术 | 理由 |
|-----|------|------|
| **前端** | HTML5 + Bootstrap 5 | 简单易用，响应式设计 |
| **图表** | Chart.js | 轻量级，功能完善 |
| **后端** | Python 3.10+ Flask | 轻量级，易于部署 |
| **ORM** | SQLAlchemy | 强大的ORM，支持多数据库 |
| **数据库** | SQLite → MySQL | 开发用SQLite，生产用MySQL |
| **认证** | Flask-Login | 简单的会话管理 |
| **表单** | Flask-WTF | 表单验证和CSRF保护 |
| **部署** | Docker + Nginx | 容器化部署，易于扩展 |

---

## 二、项目结构设计

### 2.1 目录结构

```
sales_management_system/
├── app/
│   ├── __init__.py              # Flask应用初始化
│   ├── config.py                # 配置文件
│   ├── models.py                # 数据模型（SQLAlchemy）
│   ├── forms.py                 # 表单定义
│   ├── utils.py                 # 工具函数
│   │
│   ├── api/                     # API蓝图
│   │   ├── __init__.py
│   │   ├── sales.py             # 销售相关API
│   │   ├── inventory.py         # 库存相关API
│   │   ├── reports.py           # 报表相关API
│   │   └── admin.py             # 管理相关API
│   │
│   ├── views/                   # 视图蓝图
│   │   ├── __init__.py
│   │   ├── main.py              # 主页面
│   │   ├── sales.py             # 销售管理页面
│   │   ├── inventory.py         # 库存管理页面
│   │   ├── reports.py           # 报表页面
│   │   └── admin.py             # 系统管理页面
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── sale_service.py      # 销售业务逻辑
│   │   ├── inventory_service.py # 库存业务逻辑
│   │   ├── report_service.py    # 报表业务逻辑
│   │   └── import_service.py    # 导入业务逻辑
│   │
│   ├── templates/               # Jinja2模板
│   │   ├── base.html            # 基础模板
│   │   ├── index.html           # 首页
│   │   ├── sales/               # 销售相关页面
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   └── detail.html
│   │   ├── inventory/           # 库存相关页面
│   │   │   ├── current.html
│   │   │   ├── moves.html
│   │   │   └── check.html
│   │   ├── reports/             # 报表页面
│   │   │   ├── daily.html
│   │   │   ├── customer.html
│   │   │   └── spec.html
│   │   └── admin/               # 管理页面
│   │       ├── specs.html
│   │       ├── customers.html
│   │       └── audit.html
│   │
│   └── static/                  # 静态资源
│       ├── css/
│       │   ├── main.css
│       │   └── custom.css
│       ├── js/
│       │   ├── main.js
│       │   ├── sales.js
│       │   └── charts.js
│       └── img/
│           └── logo.png
│
├── migrations/                  # 数据库迁移
│   └── versions/
│
├── tests/                       # 测试文件
│   ├── test_models.py
│   ├── test_services.py
│   └── test_api.py
│
├── scripts/                     # 脚本工具
│   ├── init_db.py              # 初始化数据库
│   ├── import_excel.py         # Excel导入工具
│   └── backup_db.py            # 数据库备份
│
├── docker/                      # Docker配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── requirements.txt             # Python依赖
├── .env.example                # 环境变量示例
├── .gitignore
├── README.md
└── run.py                      # 应用入口
```

---

## 三、核心模块设计

### 3.1 应用初始化（app/__init__.py）

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # 注册蓝图
    from app.views import main_bp, sales_bp, inventory_bp, reports_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # 注册API蓝图
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册模板过滤器
    register_template_filters(app)
    
    return app

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

def register_template_filters(app):
    """注册模板过滤器"""
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('number')
    def format_number(value, decimals=2):
        if value is None:
            return '0.00'
        return f'{value:.{decimals}f}'
```

### 3.2 配置管理（app/config.py）

```python
import os
from datetime import timedelta

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # 上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    
    # 业务配置
    DEFAULT_OPERATOR = 'Jose Burgueno'
    INVENTORY_WARNING_THRESHOLD = 100  # 库存预警阈值（KG）
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sales_dev.db'
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://user:password@localhost/sales_db'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 日志配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/sales_app.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sales Management System startup')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

### 3.3 数据模型（app/models.py）

```python
from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint

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

class Sale(db.Model):
    """销售单主表"""
    __tablename__ = 'sale'
    
    id = db.Column(db.String(50), primary_key=True)
    sale_time = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    total_kg = db.Column(db.Numeric(12, 3), default=0, nullable=False)
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
        CheckConstraint("status IN ('active','void')", 
                       name='check_status'),
    )
    
    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'sale_time': self.sale_time.isoformat(),
            'customer': self.customer.to_dict(),
            'payment_type': self.payment_type,
            'total_kg': float(self.total_kg),
            'status': self.status,
            'created_by': self.created_by
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data

class SaleItem(db.Model):
    """销售明细表"""
    __tablename__ = 'sale_item'
    
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.String(50), db.ForeignKey('sale.id'), nullable=False)
    spec_id = db.Column(db.Integer, db.ForeignKey('spec.id'), nullable=False)
    box_qty = db.Column(db.Integer, default=0, nullable=False)
    extra_kg = db.Column(db.Numeric(10, 3), default=0, nullable=False)
    subtotal_kg = db.Column(db.Numeric(12, 3), default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        CheckConstraint('box_qty >= 0', name='check_box_qty_non_negative'),
        CheckConstraint('extra_kg >= 0', name='check_extra_kg_non_negative'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'spec': self.spec.to_dict(),
            'box_qty': self.box_qty,
            'extra_kg': float(self.extra_kg),
            'subtotal_kg': float(self.subtotal_kg)
        }

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
            'move_time': self.move_time.isoformat(),
            'status': self.status
        }
```

---

## 四、业务逻辑层设计

### 4.1 销售服务（app/services/sale_service.py）

```python
from app import db
from app.models import Sale, SaleItem, Customer, Spec
from datetime import datetime
from sqlalchemy import func

class SaleService:
    """销售业务逻辑"""
    
    @staticmethod
    def generate_sale_id():
        """生成销售单号：SALE-YYYYMMDD-序号"""
        today = datetime.now().strftime('%Y%m%d')
        prefix = f'SALE-{today}-'
        
        # 查询今日最大序号
        last_sale = db.session.query(Sale).filter(
            Sale.id.like(f'{prefix}%')
        ).order_by(Sale.id.desc()).first()
        
        if last_sale:
            last_seq = int(last_sale.id.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f'{prefix}{new_seq:03d}'
    
    @staticmethod
    def create_sale(customer_id, payment_type, items_data, created_by):
        """
        创建销售单
        
        Args:
            customer_id: 客户ID
            payment_type: 支付方式
            items_data: 明细数据 [{'spec_id': 1, 'box_qty': 2, 'extra_kg': 5}, ...]
            created_by: 创建人
            
        Returns:
            Sale: 创建的销售单对象
        """
        # 验证客户
        customer = Customer.query.get(customer_id)
        if not customer:
            raise ValueError('客户不存在')
        
        if not customer.active:
            raise ValueError('客户已禁用')
        
        # 验证支付方式
        if payment_type == 'Crédito' and not customer.credit_allowed:
            raise ValueError('该客户不允许使用信用支付')
        
        # 创建销售单
        sale = Sale(
            id=SaleService.generate_sale_id(),
            sale_time=datetime.now(),
            customer_id=customer_id,
            payment_type=payment_type,
            created_by=created_by
        )
        db.session.add(sale)
        
        # 创建明细
        for item_data in items_data:
            spec = Spec.query.get(item_data['spec_id'])
            if not spec or not spec.active:
                raise ValueError(f'规格ID {item_data["spec_id"]} 不存在或已禁用')
            
            item = SaleItem(
                sale_id=sale.id,
                spec_id=item_data['spec_id'],
                box_qty=item_data.get('box_qty', 0),
                extra_kg=item_data.get('extra_kg', 0)
            )
            db.session.add(item)
        
        db.session.commit()
        
        # 刷新以获取触发器计算的值
        db.session.refresh(sale)
        
        return sale
    
    @staticmethod
    def void_sale(sale_id, void_reason, void_by):
        """作废销售单"""
        sale = Sale.query.get(sale_id)
        if not sale:
            raise ValueError('销售单不存在')
        
        if sale.status == 'void':
            raise ValueError('销售单已作废')
        
        if not void_reason:
            raise ValueError('必须填写作废原因')
        
        sale.status = 'void'
        sale.void_reason = void_reason
        sale.void_time = datetime.now()
        sale.void_by = void_by
        sale.updated_by = void_by
        sale.updated_at = datetime.now()
        
        db.session.commit()
        
        return sale
    
    @staticmethod
    def get_sales_list(page=1, per_page=20, status=None, 
                      customer_id=None, date_from=None, date_to=None):
        """获取销售单列表（分页）"""
        query = Sale.query
        
        if status:
            query = query.filter(Sale.status == status)
        
        if customer_id:
            query = query.filter(Sale.customer_id == customer_id)
        
        if date_from:
            query = query.filter(Sale.sale_time >= date_from)
        
        if date_to:
            query = query.filter(Sale.sale_time <= date_to)
        
        return query.order_by(Sale.sale_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_sale_detail(sale_id):
        """获取销售单详情"""
        sale = Sale.query.get(sale_id)
        if not sale:
            raise ValueError('销售单不存在')
        
        return sale
    
    @staticmethod
    def get_today_summary():
        """获取今日销售汇总"""
        today = datetime.now().date()
        
        result = db.session.query(
            func.count(Sale.id).label('order_count'),
            func.sum(Sale.total_kg).label('total_kg'),
            func.sum(
                db.case(
                    (Sale.payment_type == '现金', Sale.total_kg),
                    else_=0
                )
            ).label('cash_kg'),
            func.sum(
                db.case(
                    (Sale.payment_type == 'Crédito', Sale.total_kg),
                    else_=0
                )
            ).label('credit_kg')
        ).filter(
            func.date(Sale.sale_time) == today,
            Sale.status == 'active'
        ).first()
        
        return {
            'order_count': result.order_count or 0,
            'total_kg': float(result.total_kg or 0),
            'cash_kg': float(result.cash_kg or 0),
            'credit_kg': float(result.credit_kg or 0)
        }
```

### 4.2 库存服务（app/services/inventory_service.py）

```python
from app import db
from app.models import StockMove
from datetime import datetime
from sqlalchemy import func

class InventoryService:
    """库存业务逻辑"""
    
    @staticmethod
    def get_current_stock():
        """获取当前库存"""
        result = db.session.query(
            func.sum(StockMove.kg).label('current_stock')
        ).filter(
            StockMove.status == 'active'
        ).first()
        
        return float(result.current_stock or 0)
    
    @staticmethod
    def add_stock_move(move_type, source, kg, notes=None, created_by='system'):
        """添加库存变动"""
        if move_type not in ['进货', '调拨', '退货', '盘盈', '盘亏']:
            raise ValueError('无效的变动类型')
        
        # 出库类型kg应为负数
        if move_type in ['调拨', '退货', '盘亏'] and kg > 0:
            kg = -kg
        
        move = StockMove(
            move_type=move_type,
            source=source,
            kg=kg,
            move_time=datetime.now(),
            notes=notes,
            created_by=created_by
        )
        db.session.add(move)
        db.session.commit()
        
        return move
    
    @staticmethod
    def get_stock_moves(page=1, per_page=20, move_type=None, 
                       date_from=None, date_to=None):
        """获取库存变动列表"""
        query = StockMove.query.filter(StockMove.status == 'active')
        
        if move_type:
            query = query.filter(StockMove.move_type == move_type)
        
        if date_from:
            query = query.filter(StockMove.move_time >= date_from)
        
        if date_to:
            query = query.filter(StockMove.move_time <= date_to)
        
        return query.order_by(StockMove.move_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_stock_history(days=30):
        """获取库存历史趋势"""
        from datetime import timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 按日期分组统计
        moves = db.session.query(
            func.date(StockMove.move_time).label('date'),
            func.sum(StockMove.kg).label('daily_change')
        ).filter(
            StockMove.status == 'active',
            StockMove.move_time >= start_date
        ).group_by(
            func.date(StockMove.move_time)
        ).order_by('date').all()
        
        # 计算累计库存
        history = []
        cumulative = 0
        for move in moves:
            cumulative += float(move.daily_change)
            history.append({
                'date': move.date.isoformat(),
                'daily_change': float(move.daily_change),
                'cumulative_stock': cumulative
            })
        
        return history
```

---

## 五、API接口设计

### 5.1 销售API（app/api/sales.py）

```python
from flask import Blueprint, request, jsonify
from app.services.sale_service import SaleService
from app import db

sales_api = Blueprint('sales_api', __name__)

@sales_api.route('/sales', methods=['GET'])
def get_sales():
    """获取销售单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    pagination = SaleService.get_sales_list(
        page=page,
        per_page=per_page,
        status=status
    )
    
    return jsonify({
        'items': [sale.to_dict() for sale in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages
    })

@sales_api.route('/sales/<sale_id>', methods=['GET'])
def get_sale(sale_id):
    """获取销售单详情"""
    try:
        sale = SaleService.get_sale_detail(sale_id)
        return jsonify(sale.to_dict(include_items=True))
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@sales_api.route('/sales', methods=['POST'])
def create_sale():
    """创建销售单"""
    data = request.get_json()
    
    try:
        sale = SaleService.create_sale(
            customer_id=data['customer_id'],
            payment_type=data['payment_type'],
            items_data=data['items'],
            created_by=data.get('created_by', 'system')
        )
        return jsonify(sale.to_dict(include_items=True)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建失败'}), 500