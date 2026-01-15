"""
库存业务逻辑服务
"""
from app import db
from app.models import StockMove, InventoryCheck
from datetime import datetime, timedelta
from sqlalchemy import func
from app.utils import timezone

class InventoryService:
    """库存业务逻辑"""
    
    @staticmethod
    def get_current_stock():
        """
        获取当前库存
        
        Returns:
            dict: 包含current_stock_kg和last_move_time的字典
        """
        result = db.session.query(
            func.sum(StockMove.kg).label('current_stock'),
            func.max(StockMove.move_time).label('last_move_time')
        ).filter(
            StockMove.status == 'active'
        ).first()
        
        current_stock = float(result.current_stock or 0)
        
        return {
            'current_stock_kg': current_stock,
            'last_move_time': result.last_move_time,
            'warning': current_stock < 100  # 低于100kg预警
        }
    
    @staticmethod
    def get_stock_by_product():
        """
        按商品统计当前库存
        
        Returns:
            list: 每个商品的库存信息 [{'product_name': 'xxx', 'stock_kg': 100}, ...]
        """
        from app.models import PurchaseItem, SaleItem, Purchase, Sale, Product
        
        # 获取所有采购商品的总重量（按商品名称分组）
        purchase_stock = db.session.query(
            PurchaseItem.product_name,
            func.sum(PurchaseItem.kg).label('total_kg')
        ).join(
            Purchase, PurchaseItem.purchase_id == Purchase.id
        ).filter(
            Purchase.status == 'active'
        ).group_by(
            PurchaseItem.product_name
        ).all()
        
        # 获取所有销售商品的总重量（按商品名称分组）
        # SaleItem使用product_id，需要join Product表获取名称
        sale_stock = db.session.query(
            Product.name.label('product_name'),
            func.sum(SaleItem.subtotal_kg).label('total_kg')
        ).join(
            Sale, SaleItem.sale_id == Sale.id
        ).join(
            Product, SaleItem.product_id == Product.id
        ).filter(
            Sale.status == 'active'
        ).group_by(
            Product.name
        ).all()
        
        # 构建商品库存字典
        stock_dict = {}
        
        # 添加采购入库
        for item in purchase_stock:
            stock_dict[item.product_name] = float(item.total_kg or 0)
        
        # 减去销售出库
        for item in sale_stock:
            if item.product_name in stock_dict:
                stock_dict[item.product_name] -= float(item.total_kg or 0)
            else:
                stock_dict[item.product_name] = -float(item.total_kg or 0)
        
        # 转换为列表并排序
        result = [
            {
                'product_name': name,
                'stock_kg': kg
            }
            for name, kg in stock_dict.items()
        ]
        
        # 按库存量降序排序
        result.sort(key=lambda x: x['stock_kg'], reverse=True)
        
        return result
    
    @staticmethod
    def add_stock_move(move_type, source, kg, notes=None, created_by='system'):
        """
        添加库存变动
        
        Args:
            move_type: 变动类型（进货/调拨/退货/盘盈/盘亏）
            source: 来源/去向
            kg: 重量（正数为入库，负数为出库）
            notes: 备注
            created_by: 创建人
            
        Returns:
            StockMove: 创建的库存变动对象
        """
        if move_type not in ['进货', '调拨', '退货', '盘盈', '盘亏']:
            raise ValueError('无效的变动类型')
        
        # 出库类型kg应为负数
        if move_type in ['调拨', '退货', '盘亏'] and kg > 0:
            kg = -kg
        
        # 入库类型kg应为正数
        if move_type in ['进货', '盘盈'] and kg < 0:
            kg = abs(kg)
        
        move = StockMove(
            move_type=move_type,
            source=source,
            kg=kg,
            move_time=timezone.now(),
            notes=notes,
            created_by=created_by
        )
        db.session.add(move)
        db.session.commit()
        
        return move
    
    @staticmethod
    def get_stock_moves(page=1, per_page=20, move_type=None, 
                       date_from=None, date_to=None, status='active'):
        """
        获取库存变动列表
        
        Args:
            page: 页码
            per_page: 每页数量
            move_type: 变动类型过滤
            date_from: 开始日期
            date_to: 结束日期
            status: 状态过滤
            
        Returns:
            Pagination: 分页对象
        """
        query = StockMove.query
        
        if status:
            query = query.filter(StockMove.status == status)
        
        if move_type:
            query = query.filter(StockMove.move_type == move_type)
        
        if date_from:
            query = query.filter(StockMove.move_time >= date_from)
        
        if date_to:
            query = query.filter(StockMove.move_time <= date_to)
        
        return query.order_by(StockMove.move_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @staticmethod
    def get_stock_history(days=30):
        """
        获取库存历史趋势
        
        Args:
            days: 查询天数
            
        Returns:
            list: 每日库存变动历史
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 按日期分组统计
        moves = db.session.query(
            func.date(StockMove.move_time).label('date'),
            func.sum(StockMove.kg).label('daily_change')
        ).filter(
            StockMove.status == 'active',
            StockMove.move_time >= start_date
        ).group_by(
            func.date(StockMove.move_time)
        ).order_by('date').all()
        
        # 计算累计库存
        history = []
        cumulative = 0
        for move in moves:
            cumulative += float(move.daily_change)
            history.append({
                'date': move.date.isoformat(),
                'daily_change': float(move.daily_change),
                'cumulative_stock': cumulative
            })
        
        return history
    
    @staticmethod
    def get_stock_by_type():
        """
        按变动类型统计库存变动
        
        Returns:
            list: 各类型的库存变动统计
        """
        result = db.session.query(
            StockMove.move_type,
            func.count(StockMove.id).label('count'),
            func.sum(StockMove.kg).label('total_kg')
        ).filter(
            StockMove.status == 'active'
        ).group_by(
            StockMove.move_type
        ).all()
        
        return [
            {
                'move_type': row.move_type,
                'count': row.count,
                'total_kg': float(row.total_kg or 0)
            }
            for row in result
        ]
    
    @staticmethod
    def process_inventory_check(actual_kg, notes, created_by):
        """
        处理库存盘点
        
        Args:
            actual_kg: 实际库存
            notes: 备注
            created_by: 创建人
            
        Returns:
            InventoryCheck: 盘点记录对象
        """
        current_data = InventoryService.get_current_stock()
        theoretical_kg = current_data['current_stock_kg']
        difference = actual_kg - theoretical_kg
        
        # 创建盘点记录
        check = InventoryCheck(
            check_time=timezone.now(),
            actual_kg=actual_kg,
            theoretical_kg=theoretical_kg,
            difference_kg=difference,
            notes=notes,
            created_by=created_by
        )
        db.session.add(check)
        
        # 如果有差异，创建调整库存变动
        if difference != 0:
            move_type = '盘盈' if difference > 0 else '盘亏'
            
            # 使用add_stock_move方法，它会自动处理已存在的session
            # 注意：add_stock_move会commit，所以上面的check必须先被add到session中
            # 但是add_stock_move内也会add move到session
            # 由于add_stock_move最后commit，所以check也会被一起commit
            
            # 我们需要先flush check以获取ID（如果需要引用ID）
            # 但是当前add_stock_move调用时check还没commit，ID可能为空（除非auto-flush）
            db.session.flush()
            
            InventoryService.add_stock_move(
                move_type=move_type,
                source='盘点差异调整',
                kg=difference,
                notes=f"盘点自动调整 (单号: {check.id})",
                created_by=created_by
            )
            
        # add_stock_move已经commit了，如果没有差异则需要手动commit
        if difference == 0:
            db.session.commit()
            
        return check
