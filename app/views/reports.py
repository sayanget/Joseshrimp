"""
报表统计视图
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.services.report_service import ReportService
from datetime import datetime, timedelta
from app.utils.decorators import permission_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.before_request
@login_required
@permission_required('view_reports')
def before_request():
    """Protect all reports routes"""
    pass

@reports_bp.route('/')
def index():
    """报表首页"""
    # 默认显示最近30天
    date_to = datetime.now()
    date_from = date_to - timedelta(days=30)
    
    return render_template('reports/index.html',
                         date_from=date_from.strftime('%Y-%m-%d'),
                         date_to=date_to.strftime('%Y-%m-%d'))

@reports_bp.route('/daily')
def daily_sales():
    """按日期统计"""
    return render_template('reports/daily.html')

@reports_bp.route('/customer')
def customer_sales():
    """按客户统计"""
    return render_template('reports/customer.html')

@reports_bp.route('/spec')
def spec_sales():
    """按规格统计"""
    return render_template('reports/spec.html')
