"""
主页面视图
"""
from flask import Blueprint, render_template
from app.services.sale_service import SaleService
from app.services.inventory_service import InventoryService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页 - 显示今日汇总"""
    try:
        # 获取今日销售汇总
        today_summary = SaleService.get_today_summary()
        
        # 获取当前库存
        current_stock = InventoryService.get_current_stock()
        
        return render_template('index.html',
                             today_summary=today_summary,
                             current_stock=current_stock)
    except Exception as e:
        return render_template('index.html',
                             error=str(e),
                             today_summary={},
                             current_stock={})
