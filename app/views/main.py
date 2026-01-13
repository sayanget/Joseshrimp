"""
主页面视图
"""
from flask import Blueprint, render_template, jsonify, request
from app.services.sale_service import SaleService
from app.services.inventory_service import InventoryService
from datetime import datetime, date

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页 - 显示今日汇总"""
    try:
        # 获取今日销售汇总
        today_summary = SaleService.get_today_summary()
        
        # 获取当前库存
        current_stock = InventoryService.get_current_stock()
        
        # 获取分商品库存
        product_stocks = InventoryService.get_stock_by_product()
        
        return render_template('index.html',
                             today_summary=today_summary,
                             current_stock=current_stock,
                             product_stocks=product_stocks)
    except Exception as e:
        return render_template('index.html',
                             error=str(e),
                             today_summary={},
                             current_stock={})

@main_bp.route('/api/sales-summary/<date_str>')
def get_sales_summary(date_str):
    """获取指定日期的销售汇总数据"""
    try:
        # 解析日期
        sale_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 获取该日期的销售汇总
        sales, summary = SaleService.get_sales_by_date(sale_date)
        
        # 返回汇总数据
        return jsonify({
            'success': True,
            'date': date_str,
            'summary': {
                'order_count': len(sales),
                'total_kg': float(summary.get('total_kg', 0)),
                'total_amount': float(summary.get('total_amount', 0)),
                'cash_kg': float(summary.get('cash_kg', 0)),
                'cash_amount': float(summary.get('cash_amount', 0)),
                'cash_received_amount': float(summary.get('cash_amount', 0)),  # 现金销售即为已入账
                'credit_kg': float(summary.get('credit_kg', 0)),
                'credit_amount': float(summary.get('credit_amount', 0)),
                'credit_outstanding_amount': float(summary.get('credit_amount', 0) - summary.get('remittances_amount', 0))
            }
        })
    except ValueError:
        return jsonify({'success': False, 'error': '无效的日期格式'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
