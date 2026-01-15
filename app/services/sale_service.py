"""
销售业务逻辑服务
"""
from app import db
from app.models import Sale, SaleItem, Customer, Spec, StockMove, AuditLog, Product
from datetime import datetime
from sqlalchemy import func
import json
from app.utils import timezone

class SaleService:
    """销售业务逻辑"""
    
    @staticmethod
    def generate_sale_id():
        """生成销售单号：SALE-YYYYMMDD-序号"""
        today = timezone.get_current_datetime_str('%Y%m%d')
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
    def create_sale(customer_id, payment_type, items_data, created_by, discount=0, manual_total_amount=None, sale_time=None):
        """
        创建销售单
        
        Args:
            customer_id: 客户ID
            payment_type: 支付方式
            items_data: 明细数据 [{'spec_id': 1, 'box_qty': 2, 'extra_kg': 5}, ...]
            created_by: 创建人
            discount: 折扣金额
            manual_total_amount: 手动设置的总金额
            sale_time: 销售时间（可选，默认当前时间）
            
        Returns:
            Sale: 创建的销售单对象
            
        Raises:
            ValueError: 业务规则违反时抛出异常
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
        
        # 验证明细数据
        if not items_data or len(items_data) == 0:
            raise ValueError('销售明细不能为空')
        
        # 创建销售单
        # 现金销售默认为已收款，信用销售默认为未收款
        payment_status = 'paid' if payment_type == '现金' else 'unpaid'
        
        sale = Sale(
            id=SaleService.generate_sale_id(),
            sale_time=sale_time or timezone.now(),
            customer_id=customer_id,
            payment_type=payment_type,
            payment_status=payment_status,
            discount=discount,
            manual_total_amount=manual_total_amount,
            created_by=created_by
        )
        db.session.add(sale)
        
        # 创建明细
        from decimal import Decimal
        for item_data in items_data:
            spec = Spec.query.get(item_data['spec_id'])
            if not spec or not spec.active:
                raise ValueError(f'规格ID {item_data["spec_id"]} 不存在或已禁用')
            
            # 获取单价
            unit_price = None
            product_id = item_data.get('product_id')  # 商品ID(可选)
            
            if product_id:
                # 如果指定了商品,使用商品价格
                product = Product.query.get(product_id)
                if not product:
                    raise ValueError(f'商品ID {product_id} 不存在')
                if not product.active:
                    raise ValueError(f'商品 {product.name} 已禁用')
                
                # 根据支付方式选择价格
                if payment_type == '现金':
                    unit_price = product.cash_price
                elif payment_type == 'Crédito':
                    unit_price = product.credit_price
            else:
                # 如果没有指定商品,使用全局价格(向后兼容)
                from app.models import SystemConfig
                cash_price = SystemConfig.get_value('price_cash', value_type=float)
                credit_price = SystemConfig.get_value('price_credit', value_type=float)
                
                if payment_type == '现金' and cash_price:
                    unit_price = Decimal(str(cash_price))
                elif payment_type == 'Crédito' and credit_price:
                    unit_price = Decimal(str(credit_price))
            
            item = SaleItem(
                sale_id=sale.id,
                spec_id=item_data['spec_id'],
                product_id=product_id,  # 保存商品ID
                box_qty=item_data.get('box_qty', 0),
                extra_kg=Decimal(str(item_data.get('extra_kg', 0))),
                unit_price=unit_price
            )
            db.session.add(item)
        
        # 刷新一次以触发所有SaleItem的before_insert事件计算subtotal_kg
        db.session.flush()
        
        # 计算每个item的金额（如果有单价）
        for item in sale.items:
            if item.unit_price and item.subtotal_kg:
                item.total_amount = item.subtotal_kg * item.unit_price
        
        # 再次刷新以保存total_amount
        db.session.flush()
        
        # 从数据库查询确保获取最新数据
        total_kg = db.session.query(func.sum(SaleItem.subtotal_kg))\
            .filter(SaleItem.sale_id == sale.id).scalar() or 0
        calculated_subtotal_amount = db.session.query(func.sum(SaleItem.total_amount))\
            .filter(SaleItem.sale_id == sale.id).scalar() or 0
        
        sale.total_kg = total_kg
        
        # 计算最终金额
        # 如果有手动金额，直接使用
        if manual_total_amount is not None:
             sale.total_amount = manual_total_amount
        else:
             # 否则使用计算金额减去折扣
             sale.total_amount = calculated_subtotal_amount - (discount or 0)
        
        
        # 记录审计日志
        audit_log = AuditLog(
            table_name='sale',
            record_id=sale.id,
            action='INSERT',
            new_value=json.dumps({
                'id': sale.id,
                'customer_id': customer_id,
                'payment_type': payment_type
            }),
            created_by=created_by
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        # 刷新以获取触发器计算的值
        db.session.refresh(sale)
        
        return sale
    
    @staticmethod
    def void_sale(sale_id, void_reason, void_by):
        """
        作废销售单
        
        Args:
            sale_id: 销售单号
            void_reason: 作废原因
            void_by: 作废人
            
        Returns:
            Sale: 作废后的销售单对象
        """
        sale = Sale.query.get(sale_id)
        if not sale:
            raise ValueError('销售单不存在')
        
        if sale.status == 'void':
            raise ValueError('销售单已作废')
        
        if not void_reason:
            raise ValueError('必须填写作废原因')
        
        # 记录旧值
        old_value = json.dumps({
            'status': sale.status,
            'total_kg': float(sale.total_kg)
        })
        
        sale.status = 'void'
        sale.void_reason = void_reason
        sale.void_time = timezone.now()
        sale.void_by = void_by
        sale.updated_by = void_by
        sale.updated_at = timezone.now()
        
        # 记录审计日志
        audit_log = AuditLog(
            table_name='sale',
            record_id=sale.id,
            action='VOID',
            old_value=old_value,
            new_value=json.dumps({
                'status': 'void',
                'void_reason': void_reason
            }),
            created_by=void_by
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        return sale
    
    @staticmethod
    def get_sales_list(page=1, per_page=20, status=None, 
                      customer_id=None, date_from=None, date_to=None):
        """
        获取销售单列表（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            status: 状态过滤
            customer_id: 客户ID过滤
            date_from: 开始日期
            date_to: 结束日期
            
        Returns:
            Pagination: 分页对象
        """
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
        today = timezone.get_current_date()
        
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
        
        # 查询已收现金和未收信用
        sales_today = Sale.query.filter(
            func.date(Sale.sale_time) == today,
            Sale.status == 'active'
        ).all()
        
        cash_received = sum(float(s.total_amount) for s in sales_today 
                           if s.payment_type == '现金' and s.payment_status == 'paid')
        credit_outstanding = sum(float(s.total_amount) for s in sales_today 
                                if s.payment_type == 'Crédito' and s.payment_status == 'unpaid')
        total_amount = sum(float(s.total_amount) for s in sales_today)
        
        return {
            'order_count': result.order_count or 0,
            'total_kg': float(result.total_kg or 0),
            'cash_kg': float(result.cash_kg or 0),
            'credit_kg': float(result.credit_kg or 0),
            'cash_received_amount': cash_received,
            'credit_outstanding_amount': credit_outstanding,
            'total_amount': total_amount
        }
    
    @staticmethod
    def get_sales_by_date(sale_date):
        """
        获取指定日期的所有销售记录及汇总统计
        
        Args:
            sale_date: 销售日期 (date对象)
            
        Returns:
            tuple: (销售记录列表, 汇总统计字典)
        """
        from datetime import datetime, timedelta
        from app.models import Purchase, PurchaseItem, Remittance
        from decimal import Decimal
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 设置日期范围（当天00:00:00到23:59:59）
        start_datetime = datetime.combine(sale_date, datetime.min.time())
        end_datetime = datetime.combine(sale_date, datetime.max.time())
        
        logger.info(f"查询销售记录: {sale_date}, 范围: {start_datetime} 到 {end_datetime}")
        
        sales = Sale.query.filter(
            Sale.sale_time >= start_datetime,
            Sale.sale_time <= end_datetime,
            Sale.status == 'active'
        ).order_by(Sale.sale_time.desc()).all()
        
        logger.info(f"找到 {len(sales)} 条销售记录")
        
        # 调试：打印每条记录的total_kg
        for i, sale in enumerate(sales):
            logger.info(f"Sale {i+1}: ID={sale.id}, total_kg={sale.total_kg} (type={type(sale.total_kg).__name__}), float={float(sale.total_kg)}")
        
        # 计算汇总统计（显式转换为float以避免模板层面的Numeric类型问题）
        total_kg = sum(float(sale.total_kg) for sale in sales)
        total_amount = sum(float(sale.total_amount) for sale in sales)
        cash_kg = sum(float(sale.total_kg) for sale in sales if sale.payment_type == '现金')
        credit_kg = sum(float(sale.total_kg) for sale in sales if sale.payment_type == 'Crédito')
        cash_amount = sum(float(sale.total_amount) for sale in sales if sale.payment_type == '现金')
        credit_amount = sum(float(sale.total_amount) for sale in sales if sale.payment_type == 'Crédito')
        
        # 计算FIFO成本
        total_cost = SaleService.calculate_daily_cost_fifo(sale_date, total_kg)
        
        # 计算当天销售的回款金额（回款计入销售日期，而非回款日期）
        remittances_amount = SaleService.get_daily_remittances(sale_date)
        
        # 计算当天现金入账 = 现金销售 + 当天销售的回款
        daily_cash_income = cash_amount + remittances_amount
        
        # 计算利润 = 总收入 - 总成本
        profit = total_amount - total_cost
        
        summary = {
            'total_kg': total_kg,
            'total_amount': total_amount,
            'cash_kg': cash_kg,
            'credit_kg': credit_kg,
            'cash_amount': cash_amount,
            'credit_amount': credit_amount,
            'total_cost': total_cost,
            'profit': profit,
            'remittances_amount': remittances_amount,
            'daily_cash_income': daily_cash_income
        }
        
        logger.info(f"计算的汇总数据: {summary}")
        
        return sales, summary
    
    @staticmethod
    def calculate_daily_cost_fifo(sale_date, total_kg_sold):
        """
        使用FIFO方法计算指定日期销售的成本
        
        Args:
            sale_date: 销售日期 (date对象)
            total_kg_sold: 当天销售的总重量
            
        Returns:
            float: 总成本
        """
        from datetime import datetime
        from app.models import Purchase, PurchaseItem
        from decimal import Decimal
        import logging
        
        logger = logging.getLogger(__name__)
        
        if total_kg_sold <= 0:
            return 0.0
        
        # 获取销售日期之前或当天的所有采购记录，按时间升序排列（FIFO）
        end_datetime = datetime.combine(sale_date, datetime.max.time())
        
        purchases = Purchase.query.filter(
            Purchase.purchase_time <= end_datetime,
            Purchase.status == 'active'
        ).order_by(Purchase.purchase_time.asc()).all()
        
        logger.info(f"FIFO成本计算: 销售日期={sale_date}, 销售重量={total_kg_sold} KG")
        logger.info(f"找到 {len(purchases)} 个采购记录用于成本计算")
        
        total_cost = Decimal('0')
        remaining_kg = Decimal(str(total_kg_sold))
        
        # 按FIFO顺序计算成本
        for purchase in purchases:
            if remaining_kg <= 0:
                break
            
            # 获取该采购单的所有明细
            for item in purchase.items:
                if remaining_kg <= 0:
                    break
                
                # 计算该批次可用的重量
                available_kg = item.kg
                
                # 取较小值：剩余需要的重量 vs 该批次可用重量
                used_kg = min(remaining_kg, available_kg)
                
                # 计算该部分的成本
                item_cost = used_kg * item.unit_price
                total_cost += item_cost
                
                logger.info(f"  使用采购 {purchase.id} - {item.product_name}: {used_kg} KG @ ${item.unit_price}/KG = ${item_cost}")
                
                # 减少剩余需要计算的重量
                remaining_kg -= used_kg
        
        if remaining_kg > 0:
            logger.warning(f"警告: 还有 {remaining_kg} KG 无法匹配到采购记录，可能是库存不足")
        
        logger.info(f"FIFO总成本: ${total_cost}")
        
        return float(total_cost)
    
    @staticmethod
    def get_daily_remittances(sale_date):
        """
        获取指定日期销售的回款总额
        注意：回款计入销售日期，而非回款日期
        
        Args:
            sale_date: 销售日期 (date对象)
            
        Returns:
            float: 回款总额
        """
        from datetime import datetime
        from app.models import Remittance
        import logging
        
        logger = logging.getLogger(__name__)
        
        # 设置日期范围
        start_datetime = datetime.combine(sale_date, datetime.min.time())
        end_datetime = datetime.combine(sale_date, datetime.max.time())
        
        # 查询该日期销售的所有回款记录
        # 通过关联Sale表，筛选sale_time在指定日期的销售单的回款
        remittances = db.session.query(Remittance).join(
            Sale, Remittance.sale_id == Sale.id
        ).filter(
            Sale.sale_time >= start_datetime,
            Sale.sale_time <= end_datetime,
            Sale.status == 'active'
        ).all()
        
        total_remittances = sum(float(r.amount) for r in remittances)
        
        logger.info(f"日期 {sale_date} 的销售回款: 找到 {len(remittances)} 条回款记录, 总额 ${total_remittances}")
        
        return total_remittances



