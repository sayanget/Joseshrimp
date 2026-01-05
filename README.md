# 销售管理系统 - 数据库设计

## 项目概述

本项目为销售管理系统的数据库设计，严格按照开发文档要求实现，核心原则：

1. ✅ **禁止自由规格输入** - 所有规格必须来自字典表
2. ✅ **重量由系统自动计算** - 禁止人工输入总重量
3. ✅ **库存完全可追溯** - 所有库存变动可复算
4. ✅ **禁止物理删除** - 只能作废，确保对账可信性
5. ✅ **完整审计日志** - 所有关键操作可追溯

---

## 文件说明

### 1. [`database_design.md`](database_design.md)
完整的数据库设计文档，包含：
- 设计原则和业务规则
- 所有表结构详细说明
- 触发器设计
- 索引策略
- 校验规则
- 统计查询示例
- 数据迁移说明

### 2. [`schema.sql`](schema.sql)
数据库初始化脚本，包含：
- 7个核心表的创建语句
- 13个触发器（自动计算、审计日志）
- 5个统计视图
- 初始数据（常用规格和客户）
- 完整的索引和约束

### 3. [`test_database.sql`](test_database.sql)
数据库测试脚本，包含：
- 15个测试场景
- 自动计算验证
- 触发器功能测试
- 约束条件测试
- 数据完整性验证

---

## 数据库表结构

### 核心表

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| **spec** | 规格字典表 | name, kg_per_box |
| **customer** | 客户表 | name, credit_allowed |
| **sale** | 销售单主表 | id, total_kg, status |
| **sale_item** | 销售明细表 | spec_id, box_qty, subtotal_kg |
| **stock_move** | 库存变动表 | move_type, kg, status |
| **audit_log** | 审计日志表 | table_name, action, old_value, new_value |
| **inventory_check** | 盘点记录表 | actual_kg, theoretical_kg, difference_kg |

### 关系图

```
customer ──┐
           │
           ├──< sale >──< sale_item >──┤
           │                           │
           │                         spec
           │
           └──< stock_move
```

---

## 快速开始

### 1. 创建数据库

```bash
# 使用 SQLite
sqlite3 sales.db < schema.sql

# 或使用 Python
python -c "import sqlite3; conn = sqlite3.connect('sales.db'); conn.executescript(open('schema.sql').read()); conn.close()"
```

### 2. 运行测试

```bash
# 测试数据库功能
sqlite3 sales.db < test_database.sql

# 查看测试结果
sqlite3 sales.db "SELECT * FROM v_current_stock;"
```

### 3. 验证安装

```bash
# 检查表是否创建成功
sqlite3 sales.db "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

# 检查初始数据
sqlite3 sales.db "SELECT COUNT(*) as spec_count FROM spec;"
sqlite3 sales.db "SELECT COUNT(*) as customer_count FROM customer;"
```

---

## 核心功能说明

### 1. 自动重量计算

**销售明细自动计算 subtotal_kg**：
```sql
subtotal_kg = box_qty × spec.kg_per_box + extra_kg
```

**销售单自动汇总 total_kg**：
```sql
total_kg = SUM(sale_item.subtotal_kg)
```

这些计算由触发器自动完成，**禁止人工修改**。

### 2. 库存自动追溯

每笔销售自动创建库存变动记录：
```sql
-- 销售时自动创建
INSERT INTO stock_move (move_type, kg, reference_id)
VALUES ('销售', -total_kg, sale_id);
```

当前库存计算：
```sql
SELECT SUM(kg) FROM stock_move WHERE status='active';
```

### 3. 销售单作废（禁止删除）

```sql
-- 正确做法：作废
UPDATE sale 
SET status='void', void_reason='原因', void_by='操作人'
WHERE id='SALE-20260105-001';

-- 错误做法：删除（数据库不允许）
-- DELETE FROM sale WHERE id='SALE-20260105-001';  ❌
```

作废时，关联的库存变动也会自动作废。

### 4. 完整审计日志

所有关键操作自动记录：
```sql
SELECT * FROM audit_log 
WHERE table_name='sale' AND record_id='SALE-20260105-001'
ORDER BY created_at;
```

---

## 使用示例

### 创建销售单

```sql
-- 1. 创建销售单主记录
INSERT INTO sale (id, sale_time, customer_id, payment_type, created_by)
VALUES ('SALE-20260105-001', datetime('now'), 1, 'Crédito', 'Jose Burgueno');

-- 2. 添加销售明细（系统自动计算 subtotal_kg）
INSERT INTO sale_item (sale_id, spec_id, box_qty, extra_kg)
VALUES ('SALE-20260105-001', 1, 5, 10);  -- 5箱 + 10kg散货

-- 3. 查看结果（total_kg 已自动计算）
SELECT * FROM sale WHERE id='SALE-20260105-001';

-- 4. 库存变动已自动创建
SELECT * FROM stock_move WHERE reference_id='SALE-20260105-001';
```

### 查询统计

```sql
-- 今日销售汇总
SELECT * FROM v_today_sales;

-- 客户销售排名
SELECT * FROM v_customer_ranking LIMIT 10;

-- 规格使用统计
SELECT * FROM v_spec_usage ORDER BY total_kg DESC;

-- 当前库存
SELECT * FROM v_current_stock;
```

### 盘点对账

```sql
-- 1. 获取理论库存
SELECT current_stock_kg FROM v_current_stock;

-- 2. 录入实际盘点结果
INSERT INTO inventory_check (check_time, actual_kg, theoretical_kg, difference_kg, created_by)
SELECT datetime('now'), 950, current_stock_kg, 950 - current_stock_kg, 'admin'
FROM v_current_stock;

-- 3. 查看差异
SELECT * FROM inventory_check ORDER BY check_time DESC LIMIT 1;
```

---

## 数据约束和校验

### 数据库层面约束

| 约束类型 | 说明 | 示例 |
|---------|------|------|
| CHECK | 箱数和散货不能为负 | `box_qty >= 0` |
| CHECK | 单箱重量必须大于0 | `kg_per_box > 0` |
| CHECK | 支付方式限定 | `payment_type IN ('现金','Crédito')` |
| UNIQUE | 规格名称唯一 | `spec.name UNIQUE` |
| FOREIGN KEY | 外键约束 | `customer_id REFERENCES customer(id)` |

### 应用层校验（需在后端实现）

1. **销售前校验**：
   - 客户不允许信用时，禁止使用 Crédito
   - 销售后库存不能为负

2. **异常警告**：
   - 单箱重量偏差 > 10%
   - 单笔重量 > 历史均值 2倍
   - 散货占比 > 30%

---

## 常用查询

### 按日期统计销售

```sql
SELECT 
    DATE(sale_time) as sale_date,
    COUNT(*) as order_count,
    SUM(total_kg) as total_kg
FROM sale
WHERE status = 'active'
  AND sale_time >= '2026-01-01'
GROUP BY DATE(sale_time)
ORDER BY sale_date;
```

### 按客户统计

```sql
SELECT 
    c.name as customer_name,
    COUNT(s.id) as order_count,
    SUM(s.total_kg) as total_kg
FROM customer c
JOIN sale s ON c.id = s.customer_id
WHERE s.status = 'active'
GROUP BY c.id, c.name
ORDER BY total_kg DESC;
```

### 按规格统计

```sql
SELECT 
    sp.name as spec_name,
    SUM(si.box_qty) as total_boxes,
    SUM(si.subtotal_kg) as total_kg
FROM spec sp
JOIN sale_item si ON sp.id = si.spec_id
JOIN sale s ON si.sale_id = s.id
WHERE s.status = 'active'
GROUP BY sp.id, sp.name
ORDER BY total_kg DESC;
```

### 库存变动明细

```sql
SELECT 
    move_time,
    move_type,
    source,
    kg,
    reference_id,
    status
FROM stock_move
WHERE status = 'active'
ORDER BY move_time DESC;
```

---

## 数据迁移

### 从 Excel 导入数据

根据 [`table01.jpg`](table01.jpg) 中的数据结构，需要：

1. **解析描述字段**：
   - "20 KG X 110" → 查找或创建规格
   - "2 JAVAS DE 39X110" → 2箱 JAVA 39x110
   - 复杂描述需拆分为多条明细

2. **映射字段**：
   - Fecha → sale.sale_time
   - Usuario → sale.created_by
   - ID → sale.id
   - Tipo de pago → sale.payment_type
   - Contacto → customer.name

3. **创建导入脚本**（待实现）

---

## 性能优化

### 已创建的索引

```sql
-- 销售单查询
CREATE INDEX idx_sale_time ON sale(sale_time);
CREATE INDEX idx_sale_customer ON sale(customer_id);
CREATE INDEX idx_sale_status ON sale(status);

-- 销售明细查询
CREATE INDEX idx_sale_item_sale ON sale_item(sale_id);
CREATE INDEX idx_sale_item_spec ON sale_item(spec_id);

-- 库存变动查询
CREATE INDEX idx_stock_move_time ON stock_move(move_time);
CREATE INDEX idx_stock_move_status ON stock_move(status);

-- 审计日志查询
CREATE INDEX idx_audit_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_table_record ON audit_log(table_name, record_id);
```

---

## 备份与恢复

### 备份数据库

```bash
# SQLite 备份
sqlite3 sales.db ".backup sales_backup_$(date +%Y%m%d).db"

# 或导出为 SQL
sqlite3 sales.db .dump > sales_backup_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
# 从备份文件恢复
cp sales_backup_20260105.db sales.db

# 从 SQL 文件恢复
sqlite3 sales_new.db < sales_backup_20260105.sql
```

---

## 安全性

### 权限控制（应用层实现）

| 角色 | 权限 |
|------|------|
| 操作员 | 创建销售单、查看统计 |
| 管理员 | 作废销售单、维护规格、查看审计日志 |

### 数据保护

1. **禁止物理删除**：sale、stock_move 表禁止 DELETE
2. **审计日志不可修改**：audit_log 表只能 INSERT
3. **计算字段保护**：total_kg、subtotal_kg 由触发器控制

---

## 监控与告警

### 建议监控指标

1. **库存异常**：库存 < 0
2. **差异过大**：盘点差异 > 50kg
3. **异常订单**：单笔重量 > 历史均值 2倍
4. **散货占比**：散货 > 30%

### 定期报告

1. 每日库存报告
2. 每周销售汇总
3. 每月对账报告

---

## 故障排查

### 常见问题

**Q: total_kg 没有自动计算？**
```sql
-- 检查触发器是否存在
SELECT name FROM sqlite_master WHERE type='trigger';

-- 手动触发计算
UPDATE sale 
SET total_kg = (SELECT SUM(subtotal_kg) FROM sale_item WHERE sale_id = sale.id)
WHERE id = 'SALE-20260105-001';
```

**Q: 库存变动没有自动创建？**
```sql
-- 检查销售单状态
SELECT id, status, total_kg FROM sale WHERE id = 'SALE-20260105-001';

-- 检查是否已存在
SELECT * FROM stock_move WHERE reference_id = 'SALE-20260105-001';
```

**Q: 如何查看某个销售单的完整历史？**
```sql
SELECT * FROM audit_log 
WHERE table_name = 'sale' AND record_id = 'SALE-20260105-001'
ORDER BY created_at;
```

---

## 下一步开发

### 待实现功能

1. ✅ 数据库设计完成
2. ⏳ Python/Flask 后端实现
3. ⏳ Web 前端界面
4. ⏳ Excel 数据导入工具
5. ⏳ 报表导出功能
6. ⏳ 用户认证系统

### 技术栈建议

- **后端**：Python Flask + SQLAlchemy
- **前端**：HTML + Bootstrap（简单表单）
- **数据库**：SQLite（开发） → MySQL（生产）
- **部署**：Docker + Nginx

---

## 联系方式

如有问题或建议，请联系开发团队。

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-01-05 | 初始版本，完成数据库设计 |

---

## 许可证

本项目为内部使用，保留所有权利。
