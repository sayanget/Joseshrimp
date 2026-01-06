"""
Excel导出工具

提供各种报表的Excel导出功能
"""
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from flask import make_response
from io import BytesIO
from datetime import datetime

class ExcelExporter:
    """Excel导出器"""
    
    @staticmethod
    def create_workbook(title="Report"):
        """创建工作簿"""
        wb = Workbook()
        ws = wb.active
        ws.title = title
        return wb, ws
    
    @staticmethod
    def style_header(ws, row=1):
        """设置表头样式"""
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in ws[row]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
    
    @staticmethod
    def auto_adjust_column_width(ws):
        """自动调整列宽"""
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    @staticmethod
    def export_daily_sales(data, date_from, date_to):
        """导出每日销售报表"""
        wb, ws = ExcelExporter.create_workbook("Daily Sales")
        
        # 标题
        ws['A1'] = f'Daily Sales Report ({date_from} to {date_to})'
        ws.merge_cells('A1:F1')
        ws['A1'].font = Font(size=14, bold=True)
        ws['A1'].alignment = Alignment(horizontal="center")
        
        # 表头
        headers = ['Date', 'Orders', 'Total KG', 'Cash KG', 'Credit KG', 'Total Amount ($)']
        ws.append([])  # 空行
        ws.append(headers)
        ExcelExporter.style_header(ws, row=3)
        
        # 数据
        for row in data:
            ws.append([
                row['date'],
                row['order_count'],
                round(row['total_kg'], 2),
                round(row['cash_kg'], 2),
                round(row['credit_kg'], 2),
                round(row.get('total_amount', 0), 2)
            ])
        
        ExcelExporter.auto_adjust_column_width(ws)
        
        return ExcelExporter.create_response(wb, f'daily_sales_{date_from}_{date_to}.xlsx')
    
    @staticmethod
    def export_customer_sales(data, date_from=None, date_to=None):
        """导出客户销售排名"""
        wb, ws = ExcelExporter.create_workbook("Customer Sales")
        
        # 标题
        period = f' ({date_from} to {date_to})' if date_from and date_to else ''
        ws['A1'] = f'Customer Sales Ranking{period}'
        ws.merge_cells('A1:F1')
        ws['A1'].font = Font(size=14, bold=True)
        ws['A1'].alignment = Alignment(horizontal="center")
        
        # 表头
        headers = ['Rank', 'Customer', 'Orders', 'Total KG', 'Total Amount ($)', 'Last Sale']
        ws.append([])
        ws.append(headers)
        ExcelExporter.style_header(ws, row=3)
        
        # 数据
        for idx, row in enumerate(data, 1):
            ws.append([
                idx,
                row['customer_name'],
                row['order_count'],
                round(row['total_kg'], 2),
                round(row.get('total_amount', 0), 2),
                row.get('last_sale', '')
            ])
        
        ExcelExporter.auto_adjust_column_width(ws)
        
        return ExcelExporter.create_response(wb, f'customer_sales_{datetime.now().strftime("%Y%m%d")}.xlsx')
    
    @staticmethod
    def export_spec_sales(data, date_from=None, date_to=None):
        """导出规格使用统计"""
        wb, ws = ExcelExporter.create_workbook("Spec Sales")
        
        # 标题
        period = f' ({date_from} to {date_to})' if date_from and date_to else ''
        ws['A1'] = f'Specification Usage Ranking{period}'
        ws.merge_cells('A1:F1')
        ws['A1'].font = Font(size=14, bold=True)
        ws['A1'].alignment = Alignment(horizontal="center")
        
        # 表头
        headers = ['Rank', 'Specification', 'Usage Count', 'Total Boxes', 'Extra KG', 'Total KG']
        ws.append([])
        ws.append(headers)
        ExcelExporter.style_header(ws, row=3)
        
        # 数据
        for idx, row in enumerate(data, 1):
            ws.append([
                idx,
                row['spec_name'],
                row['usage_count'],
                row['total_boxes'],
                round(row['extra_kg'], 2),
                round(row['total_kg'], 2)
            ])
        
        ExcelExporter.auto_adjust_column_width(ws)
        
        return ExcelExporter.create_response(wb, f'spec_sales_{datetime.now().strftime("%Y%m%d")}.xlsx')
    
    @staticmethod
    def create_response(wb, filename):
        """创建Flask响应"""
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
