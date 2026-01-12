"""
回款业务逻辑服务
"""
from app import db
from app.models import Sale, Remittance, AuditLog
from datetime import datetime
from decimal import Decimal
from sqlalchemy import func
import json


class RemittanceService:
    """回款业务逻辑"""
    
    @staticmethod
    def get_credit_sales_list(page=1, per_page=20, payment_status=None):
        """
        获取信用结算记录列表
        
        Args:
            page: 页码
            per_page: 每页数量
            payment_status: 收款状态过滤 (unpaid/partial)
            
        Returns:
            Pagination: 分页对象，包含销售单及回款信息
        """
        query = Sale.query.filter(
            Sale.payment_type == 'Crédito',
            Sale.status == 'active'
        )
        
        # 过滤收款状态
        if payment_status:
            query = query.filter(Sale.payment_status == payment_status)
        else:
            # 默认只显示未完全回款的记录
            query = query.filter(Sale.payment_status.in_(['unpaid', 'partial']))
        
        # 按销售时间倒序排列
        query = query.order_by(Sale.sale_time.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 为每个销售单计算已回款金额和未回款金额
        for sale in pagination.items:
            paid_amount = db.session.query(func.sum(Remittance.amount))\
                .filter(Remittance.sale_id == sale.id)\
                .scalar() or Decimal('0')
            
            sale.paid_amount = float(paid_amount)
            sale.unpaid_amount = float(sale.total_amount - paid_amount)
        
        return pagination
    
    @staticmethod
    def create_remittance(sale_id, amount, created_by, notes=None, remittance_time=None):
        """
        创建回款记录并更新相关数据
        
        Args:
            sale_id: 销售单号
            amount: 回款金额
            created_by: 创建人
            notes: 备注
            remittance_time: 回款时间（默认当前时间）
            
        Returns:
            Remittance: 回款记录对象
            
        Raises:
            ValueError: 业务规则违反时抛出异常
        """
        # 1. 验证销售单
        sale = Sale.query.get(sale_id)
        if not sale:
            raise ValueError(f"销售单 {sale_id} 不存在")
        
        if sale.status != 'active':
            raise ValueError("只能对有效的销售单进行回款")
        
        if sale.payment_type != 'Crédito':
            raise ValueError("只能对信用销售进行回款")
        
        if sale.payment_status == 'paid':
            raise ValueError("该销售单已全额回款")
        
        # 2. 计算已回款金额
        paid_amount = db.session.query(func.sum(Remittance.amount))\
            .filter(Remittance.sale_id == sale_id)\
            .scalar() or Decimal('0')
        
        unpaid_amount = sale.total_amount - paid_amount
        
        # 3. 验证回款金额
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("回款金额必须大于0")
        
        if amount_decimal > unpaid_amount:
            raise ValueError(f"回款金额不能超过未回款金额 ${float(unpaid_amount):.2f}")
        
        # 4. 创建回款记录
        remittance = Remittance(
            sale_id=sale_id,
            amount=amount_decimal,
            notes=notes,
            remittance_time=remittance_time or datetime.utcnow(),
            created_by=created_by
        )
        db.session.add(remittance)
        
        # 5. 更新销售单收款状态
        new_paid_amount = paid_amount + amount_decimal
        if new_paid_amount >= sale.total_amount:
            sale.payment_status = 'paid'
        else:
            sale.payment_status = 'partial'
        
        sale.updated_by = created_by
        sale.updated_at = datetime.utcnow()
        
        # 6. 记录审计日志
        audit_log = AuditLog(
            table_name='remittance',
            record_id=str(remittance.id) if remittance.id else 'pending',
            action='INSERT',
            new_value=json.dumps({
                'sale_id': sale_id,
                'amount': float(amount_decimal),
                'payment_status': sale.payment_status,
                'notes': notes
            }),
            created_by=created_by
        )
        db.session.add(audit_log)
        
        # 7. 提交事务
        try:
            db.session.commit()
            
            # 更新审计日志的record_id
            if audit_log.record_id == 'pending':
                audit_log.record_id = str(remittance.id)
                db.session.commit()
                
            return remittance
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"创建回款记录失败: {str(e)}")
    
    @staticmethod
    def get_remittance_history(sale_id):
        """
        获取某销售单的回款历史
        
        Args:
            sale_id: 销售单号
            
        Returns:
            list: 回款记录列表
        """
        remittances = Remittance.query.filter_by(sale_id=sale_id)\
            .order_by(Remittance.remittance_time.desc())\
            .all()
        
        return [r.to_dict() for r in remittances]
    
    @staticmethod
    def get_remittance_summary(sale_id):
        """
        获取销售单的回款汇总信息
        
        Args:
            sale_id: 销售单号
            
        Returns:
            dict: 回款汇总信息
        """
        sale = Sale.query.get(sale_id)
        if not sale:
            raise ValueError(f"销售单 {sale_id} 不存在")
        
        paid_amount = db.session.query(func.sum(Remittance.amount))\
            .filter(Remittance.sale_id == sale_id)\
            .scalar() or Decimal('0')
        
        remittance_count = Remittance.query.filter_by(sale_id=sale_id).count()
        
        return {
            'sale_id': sale_id,
            'total_amount': float(sale.total_amount),
            'paid_amount': float(paid_amount),
            'unpaid_amount': float(sale.total_amount - paid_amount),
            'payment_status': sale.payment_status,
            'remittance_count': remittance_count
        }
