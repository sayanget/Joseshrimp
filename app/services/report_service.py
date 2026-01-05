"""
报表统计业务逻辑服务
"""
from app import db
from app.models import Sale, SaleItem, Customer, Spec
from datetime import datetime, timedelta
from sqlalchemy import func

class ReportService:
    """报表统计业务逻辑"""
    
    @staticmethod
    def get_daily_sales(date_from, date_to):
        """
        按日期统计销售
        
        Args:
            date_from: 开始日期
            date_to: 结束日期
            
        Returns:
            list: 每日销售统计数据
        """
        result = db.session.query(
            func.date(Sale.sale_time).label('date'),
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
            Sale.status == 'active',
            Sale.sale_time >= date_from,
            Sale.sale_time <= date_to
        ).group_by(
            func.date(Sale.sale_time)
        ).order_by('date').all()
        
        return [
            {
                'date': row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                'order_count': row.order_count,
                'total_kg': float(row.total_kg or 0),
                'cash_kg': float(row.cash_kg or 0),
                'credit_kg': float(row.credit_kg or 0)
            }
            for row in result
        ]
    
    @staticmethod
    def get_customer_sales(date_from=None, date_to=None, limit=10):
        """
        按客户统计销售
        
        Args:
            date_from: 开始日期
            date_to: 结束日期
            limit: 返回数量
            
        Returns:
            list: 客户销售统计数据
        """
        query = db.session.query(
            Customer.id.label('customer_id'),
            Customer.name.label('customer_name'),
            func.count(Sale.id).label('order_count'),
            func.sum(Sale.total_kg).label('total_kg'),
            func.avg(Sale.total_kg).label('avg_kg_per_order'),
            func.max(Sale.sale_time).label('last_sale_time')
        ).join(
            Sale, Customer.id == Sale.customer_id
        ).filter(
            Sale.status == 'active'
        )
        
        if date_from:
            query = query.filter(Sale.sale_time >= date_from)
        
        if date_to:
            query = query.filter(Sale.sale_time <= date_to)
        
        result = query.group_by(
            Customer.id, Customer.name
        ).order_by(
            func.sum(Sale.total_kg).desc()
        ).limit(limit).all()
        
        return [
            {
                'customer_id': row.customer_id,
                'customer_name': row.customer_name,
                'order_count': row.order_count,
                'total_kg': float(row.total_kg or 0),
                'avg_kg_per_order': float(row.avg_kg_per_order or 0),
                'last_sale_time': row.last_sale_time.isoformat() if row.last_sale_time and hasattr(row.last_sale_time, 'isoformat') else (str(row.last_sale_time) if row.last_sale_time else None)
            }
            for row in result
        ]
    
    @staticmethod
    def get_spec_sales(date_from=None, date_to=None, limit=10):
        """
        按规格统计销售
        
        Args:
            date_from: 开始日期
            date_to: 结束日期
            limit: 返回数量
            
        Returns:
            list: 规格销售统计数据
        """
        query = db.session.query(
            Spec.id.label('spec_id'),
            Spec.name.label('spec_name'),
            Spec.kg_per_box,
            func.count(SaleItem.id).label('usage_count'),
            func.sum(SaleItem.box_qty).label('total_boxes'),
            func.sum(SaleItem.extra_kg).label('total_extra_kg'),
            func.sum(SaleItem.subtotal_kg).label('total_kg')
        ).join(
            SaleItem, Spec.id == SaleItem.spec_id
        ).join(
            Sale, SaleItem.sale_id == Sale.id
        ).filter(
            Sale.status == 'active'
        )
        
        if date_from:
            query = query.filter(Sale.sale_time >= date_from)
        
        if date_to:
            query = query.filter(Sale.sale_time <= date_to)
        
        result = query.group_by(
            Spec.id, Spec.name, Spec.kg_per_box
        ).order_by(
            func.sum(SaleItem.subtotal_kg).desc()
        ).limit(limit).all()
        
        return [
            {
                'spec_id': row.spec_id,
                'spec_name': row.spec_name,
                'kg_per_box': float(row.kg_per_box),
                'usage_count': row.usage_count,
                'total_boxes': row.total_boxes or 0,
                'total_extra_kg': float(row.total_extra_kg or 0),
                'total_kg': float(row.total_kg or 0)
            }
            for row in result
        ]
    
    @staticmethod
    def get_extra_kg_analysis(date_from=None, date_to=None, min_percent=0):
        """
        散货占比分析
        
        Args:
            date_from: 开始日期
            date_to: 结束日期
            min_percent: 最小占比（百分比）
            
        Returns:
            list: 散货占比分析数据
        """
        # 子查询：计算每个销售单的散货总量
        subquery = db.session.query(
            SaleItem.sale_id,
            func.sum(SaleItem.extra_kg).label('extra_kg')
        ).group_by(SaleItem.sale_id).subquery()
        
        query = db.session.query(
            Sale.id.label('sale_id'),
            Sale.sale_time,
            Customer.name.label('customer_name'),
            Sale.total_kg,
            subquery.c.extra_kg,
            (subquery.c.extra_kg * 100.0 / Sale.total_kg).label('extra_percent')
        ).join(
            Customer, Sale.customer_id == Customer.id
        ).join(
            subquery, Sale.id == subquery.c.sale_id
        ).filter(
            Sale.status == 'active',
            Sale.total_kg > 0
        )
        
        if date_from:
            query = query.filter(Sale.sale_time >= date_from)
        
        if date_to:
            query = query.filter(Sale.sale_time <= date_to)
        
        if min_percent > 0:
            query = query.filter(
                (subquery.c.extra_kg * 100.0 / Sale.total_kg) >= min_percent
            )
        
        result = query.order_by(
            (subquery.c.extra_kg * 100.0 / Sale.total_kg).desc()
        ).all()
        
        return [
            {
                'sale_id': row.sale_id,
                'sale_time': row.sale_time.isoformat() if row.sale_time and hasattr(row.sale_time, 'isoformat') else (str(row.sale_time) if row.sale_time else None),
                'customer_name': row.customer_name,
                'total_kg': float(row.total_kg),
                'extra_kg': float(row.extra_kg or 0),
                'extra_percent': round(float(row.extra_percent or 0), 2)
            }
            for row in result
        ]
    
    @staticmethod
    def get_summary_stats(date_from=None, date_to=None):
        """
        获取汇总统计数据
        
        Args:
            date_from: 开始日期
            date_to: 结束日期
            
        Returns:
            dict: 汇总统计数据
        """
        query = db.session.query(Sale).filter(Sale.status == 'active')
        
        if date_from:
            query = query.filter(Sale.sale_time >= date_from)
        
        if date_to:
            query = query.filter(Sale.sale_time <= date_to)
        
        total_orders = query.count()
        total_kg = db.session.query(func.sum(Sale.total_kg)).filter(
            Sale.status == 'active'
        )
        
        if date_from:
            total_kg = total_kg.filter(Sale.sale_time >= date_from)
        if date_to:
            total_kg = total_kg.filter(Sale.sale_time <= date_to)
        
        total_kg = total_kg.scalar() or 0
        
        # 统计客户数量
        customer_count = db.session.query(func.count(func.distinct(Sale.customer_id))).filter(
            Sale.status == 'active'
        )
        if date_from:
            customer_count = customer_count.filter(Sale.sale_time >= date_from)
        if date_to:
            customer_count = customer_count.filter(Sale.sale_time <= date_to)
        
        customer_count = customer_count.scalar() or 0
        
        return {
            'total_orders': total_orders,
            'total_kg': float(total_kg),
            'avg_kg_per_order': float(total_kg / total_orders) if total_orders > 0 else 0,
            'customer_count': customer_count
        }
