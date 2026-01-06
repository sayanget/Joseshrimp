"""
Flask应用初始化模块
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_babel import Babel
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from app.config import config

db = SQLAlchemy()
babel = Babel()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)  # 允许跨域请求
    babel.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # 配置LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    from app.models import AnonymousUser
    login_manager.anonymous_user = AnonymousUser
    
    # 配置Babel语言选择器
    def get_locale():
        from flask import request, session
        # 优先使用session中的语言设置
        if 'language' in session:
            return session['language']
        # 其次使用URL参数
        lang = request.args.get('lang')
        if lang in app.config['BABEL_SUPPORTED_LOCALES']:
            return lang
        # 最后使用浏览器语言
        return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES']) or app.config['BABEL_DEFAULT_LOCALE']
    
    babel.init_app(app, locale_selector=get_locale)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 注册模板过滤器
    register_template_filters(app)
    
    return app

def register_blueprints(app):
    """注册蓝图"""
    # 视图蓝图
    from app.views.main import main_bp
    from app.views.sales import sales_bp
    from app.views.inventory import inventory_bp
    from app.views.reports import reports_bp
    from app.views.admin import admin_bp
    from app.views.language import language_bp
    from app.auth import auth_bp
    
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(sales_bp, url_prefix='/sales')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(language_bp, url_prefix='/language')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # API蓝图
    from app.api.sales import sales_api
    from app.api.inventory import inventory_api
    from app.api.reports import reports_api
    from app.api.admin import admin_api
    
    app.register_blueprint(sales_api, url_prefix='/api/sales')
    app.register_blueprint(inventory_api, url_prefix='/api/inventory')
    app.register_blueprint(reports_api, url_prefix='/api/reports')
    app.register_blueprint(admin_api, url_prefix='/api/admin')

def register_error_handlers(app):
    """注册错误处理器"""
    from flask import render_template, jsonify, request
    
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': '资源不存在'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': '服务器内部错误'}), 500
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
        if value is None or value == '':
            return '0.00'
        try:
            return f'{float(value):.{decimals}f}'
        except (ValueError, TypeError):
            return '0.00'
    
    @app.template_filter('date')
    def format_date(value):
        if value is None:
            return ''
        return value.strftime('%Y-%m-%d')
