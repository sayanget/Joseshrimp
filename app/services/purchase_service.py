"""
采购业务逻辑服务
"""
from app import db
from app.models import Purchase, PurchaseItem, Product, StockMove, AuditLog
from datetime import datetime
from sqlalchemy import func
from decimal import Decimal
import json
from app.utils import timezone

class PurchaseService:
    """采购业务逻辑"""
    
    @staticmethod
    def generate_purchase_id():
        """生成采购单号：PURCH-YYYYMMDD-序号"""
        today = timezone.get_current_datetime_str('%Y%m%d')
        prefix = f'PURCH-{today}-'
        
        # 查询今日最大序号
        last_purchase = db.session.query(Purchase).filter(
            Purchase.id.like(f'{prefix}%')
        ).order_by(Purchase.id.desc()).first()
        
        if last_purchase:
            last_seq = int(last_purchase.id.split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        
        return f'{prefix}{new_seq:03d}'
    
    @staticmethod
    def create_purchase(supplier, items_data, created_by, purchase_time=None, notes=None):
        """
        创建采购单
        
        Args:
            supplier: 供应商名称
            items_data: 明细数据 [{'product_name': 'xxx', 'kg': 10, 'unit_price': 5.5}, ...]
            created_by: 创建人
            purchase_time: 采购时间（可选，默认当前时间）
            notes: 备注（可选）
            
        Returns:
            Purchase: 创建的采购单对象
            
        Raises:
            ValueError: 业务规则违反时抛出异常
        """
        # 验证明细数据
        if not items_data or len(items_data) == 0:
            raise ValueError('采购明细不能为空')
        
        # 创建采购单
        purchase = Purchase(
            id=PurchaseService.generate_purchase_id(),
            purchase_time=purchase_time or timezone.now(),
            supplier=supplier,
            notes=notes,
            created_by=created_by
        )
        db.session.add(purchase)
        
        # 创建明细
        for item_data in items_data:
            if not item_data.get('product_name'):
                raise ValueError('商品名称不能为空')
            if not item_data.get('kg') or float(item_data['kg']) <= 0:
                raise ValueError('重量必须大于0')
            if not item_data.get('unit_price') or float(item_data['unit_price']) <= 0:
                raise ValueError('单价必须大于0')
            
            kg = Decimal(str(item_data['kg']))
            unit_price = Decimal(str(item_data['unit_price']))
            total_amount = kg * unit_price
            
            item = PurchaseItem(
                purchase_id=purchase.id,
                product_name=item_data['product_name'],
                kg=kg,
                unit_price=unit_price,
                total_amount=total_amount
            )
            db.session.add(item)
        
        # 刷新以获取所有items
        db.session.flush()
        
        # 从数据库查询确保获取最新数据
        total_kg = db.session.query(func.sum(PurchaseItem.kg))\
            .filter(PurchaseItem.purchase_id == purchase.id).scalar() or 0
        total_amount = db.session.query(func.sum(PurchaseItem.total_amount))\
            .filter(PurchaseItem.purchase_id == purchase.id).scalar() or 0
        
        purchase.total_kg = total_kg
        purchase.total_amount = total_amount
        
        # 创建库存变动记录
        stock_move = StockMove(
            move_type='进货',
            source=supplier,
            kg=total_kg,
            move_time=purchase.purchase_time,
            reference_id=purchase.id,
            reference_type='purchase',
            notes=f'采购入库: {supplier}',
            created_by=created_by
        )
        db.session.add(stock_move)
        
        # 自动创建/更新Product记录
        for item in purchase.items:
            product = Product.query.filter_by(name=item.product_name).first()
            if not product:
                # 创建新商品
                product = Product(
                    name=item.product_name,
                    cash_price=item.unit_price,
                    credit_price=item.unit_price,
                    active=True,
                    created_by=created_by
                )
                db.session.add(product)
        
        # 记录审计日志
        audit_log = AuditLog(
            table_name='purchase',
            record_id=purchase.id,
            action='INSERT',
            new_value=json.dumps({
                'id': purchase.id,
                'supplier': supplier,
                'total_kg': float(total_kg),
                'total_amount': float(total_amount)
            }),
            created_by=created_by
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        # 刷新以获取最新值
        db.session.refresh(purchase)
        
        return purchase
    
    @staticmethod
    def get_purchase_list(page=1, per_page=20, status='active'):
        """
        获取采购单列表（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            status: 状态过滤
            
        Returns:
            Pagination: 分页对象
        """
        query = Purchase.query
        
        if status:
            query = query.filter(Purchase.status == status)
        
        return query.order_by(Purchase.purchase_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_purchase_detail(purchase_id):
        """获取采购单详情"""
        purchase = Purchase.query.get(purchase_id)
        if not purchase:
            raise ValueError('采购单不存在')
        
        return purchase
