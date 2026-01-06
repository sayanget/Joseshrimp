"""
报表统计 API
"""
from flask import Blueprint, request, jsonify
from app.services.report_service import ReportService
from datetime import datetime

reports_api = Blueprint('reports_api', __name__)

@reports_api.route('/daily-sales', methods=['GET'])
def get_daily_sales():
    """按日期统计销售"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if not date_from or not date_to:
            return jsonify({'error': '开始日期和结束日期不能为空'}), 400
        
        # 转换日期
        date_from = datetime.fromisoformat(date_from)
        date_to = datetime.fromisoformat(date_to)
        
        data = ReportService.get_daily_sales(date_from, date_to)
        return jsonify({'data': data})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_api.route('/customer-sales', methods=['GET'])
def get_customer_sales():
    """按客户统计销售"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 10, type=int)
        
        # 转换日期
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        
        data = ReportService.get_customer_sales(date_from, date_to, limit)
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_api.route('/spec-sales', methods=['GET'])
def get_spec_sales():
    """按规格统计销售"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 10, type=int)
        
        # 转换日期
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        
        data = ReportService.get_spec_sales(date_from, date_to, limit)
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_api.route('/extra-kg-analysis', methods=['GET'])
def get_extra_kg_analysis():
    """散货占比分析"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        min_percent = request.args.get('min_percent', 0, type=float)
        
        # 转换日期
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        
        data = ReportService.get_extra_kg_analysis(date_from, date_to, min_percent)
        return jsonify({'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_api.route('/summary', methods=['GET'])
def get_summary_stats():
    """获取汇总统计"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # 转换日期
        if date_from:
            date_from = datetime.fromisoformat(date_from)
        if date_to:
            date_to = datetime.fromisoformat(date_to)
        
        data = ReportService.get_summary_stats(date_from, date_to)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Excel导出 ====================

@reports_api.route('/export/daily-sales', methods=['GET'])
def export_daily_sales():
    """导出每日销售报表"""
    try:
        from app.utils.excel_exporter import ExcelExporter
        
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        if not date_from or not date_to:
            return jsonify({'error': '开始日期和结束日期不能为空'}), 400
        
        # 转换日期
        date_from_obj = datetime.fromisoformat(date_from)
        date_to_obj = datetime.fromisoformat(date_to)
        
        data = ReportService.get_daily_sales(date_from_obj, date_to_obj)
        return ExcelExporter.export_daily_sales(data, date_from, date_to)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_api.route('/export/customer-sales', methods=['GET'])
def export_customer_sales():
    """导出客户销售排名"""
    try:
        from app.utils.excel_exporter import ExcelExporter
        
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 100, type=int)  # 导出时默认100条
        
        # 转换日期
        date_from_obj = None
        date_to_obj = None
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from)
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to)
        
        data = ReportService.get_customer_sales(date_from_obj, date_to_obj, limit)
        return ExcelExporter.export_customer_sales(data, date_from, date_to)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_api.route('/export/spec-sales', methods=['GET'])
def export_spec_sales():
    """导出规格使用统计"""
    try:
        from app.utils.excel_exporter import ExcelExporter
        
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        limit = request.args.get('limit', 100, type=int)
        
        # 转换日期
        date_from_obj = None
        date_to_obj = None
        if date_from:
            date_from_obj = datetime.fromisoformat(date_from)
        if date_to:
            date_to_obj = datetime.fromisoformat(date_to)
        
        data = ReportService.get_spec_sales(date_from_obj, date_to_obj, limit)
        return ExcelExporter.export_spec_sales(data, date_from, date_to)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
