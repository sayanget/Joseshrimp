# 数据库设计文档

## 一、设计原则

根据开发文档要求，本数据库设计遵循以下核心原则：

1. **严格按开发文档实现系统**
2. **不得自行抽象业务模型**
3. **不得允许自由规格输入** - 所有规格必须来自字典表
4. **重量只能由后端计算** - 禁止人工输入总重量
5. **库存必须可追溯可复算** - 所有库存变动可追溯
6. **禁止任何破坏对账可信性的快捷方案** - 禁止删除，只允许作废

---

## 二、数据库表结构设计

### 2.1 规格表（spec）

**用途**：存储所有产品规格，禁止自由输入规格文本

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键 |
| name | VARCHAR(100) | NOT NULL UNIQUE | 规格名称，如：JAVA 39x110 |
| length | INTEGER | NOT NULL | 长度（cm） |
| width | INTEGER | NOT NULL | 宽度（cm） |
| kg_per_box | DECIMAL(10,3) | NOT NULL CHECK(kg_per_box > 0) | 单箱标准重量（KG） |
| active | BOOLEAN | NOT NULL DEFAULT 1 | 是否启用 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| created_by | VARCHAR(50) | NOT NULL | 创建人 |
| updated_at | DATETIME | NULL | 更新时间 |
| updated_by | VARCHAR(50) | NULL | 更新人 |

**索引**：
- PRIMARY KEY (id)
- UNIQUE INDEX idx_spec_name (name)
- INDEX idx_spec_active (active)

**业务规则**：
- 规格名称必须唯一
- 单箱重量必须大于0
- 禁用规格不能删除，只能设置 active=0

---

### 2.2 客户表（customer）

**用途**：存储客户信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键 |
| name | VARCHAR(100) | NOT NULL UNIQUE | 客户名称 |
| credit_allowed | BOOLEAN | NOT NULL DEFAULT 0 | 是否允许信用支付 |
| active | BOOLEAN | NOT NULL DEFAULT 1 | 是否启用 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| created_by | VARCHAR(50) | NOT NULL | 创建人 |
| updated_at | DATETIME | NULL | 更新时间 |
| updated_by | VARCHAR(50) | NULL | 更新人 |

**索引**：
- PRIMARY KEY (id)
- UNIQUE INDEX idx_customer_name (name)
- INDEX idx_customer_active (active)

**业务规则**：
- 客户名称必须唯一
- 如果 credit_allowed=0，则不能使用 Crédito 支付方式

---

### 2.3 销售单主表（sale）

**用途**：存储销售单主信息

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(50) | PRIMARY KEY | 单据号，格式：SALE-YYYYMMDD-序号 |
| sale_time | DATETIME | NOT NULL | 销售时间 |
| customer_id | INTEGER | NOT NULL | 客户ID |
| payment_type | VARCHAR(20) | NOT NULL CHECK(payment_type IN ('现金','Crédito')) | 支付方式 |
| total_kg | DECIMAL(12,3) | NOT NULL DEFAULT 0 | 总重量（自动汇总，禁止人工输入） |
| status | VARCHAR(20) | NOT NULL DEFAULT 'active' CHECK(status IN ('active','void')) | 状态：active-有效，void-作废 |
| void_reason | TEXT | NULL | 作废原因 |
| void_time | DATETIME | NULL | 作废时间 |
| void_by | VARCHAR(50) | NULL | 作废人 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| created_by | VARCHAR(50) | NOT NULL | 创建人（操作员） |
| updated_at | DATETIME | NULL | 更新时间 |
| updated_by | VARCHAR(50) | NULL | 更新人 |

**外键**：
- FOREIGN KEY (customer_id) REFERENCES customer(id)

**索引**：
- PRIMARY KEY (id)
- INDEX idx_sale_time (sale_time)
- INDEX idx_sale_customer (customer_id)
- INDEX idx_sale_status (status)
- INDEX idx_sale_created_by (created_by)

**业务规则**：
- total_kg 由系统自动计算，禁止人工修改
- 销售单禁止物理删除，只能作废（status='void'）
- 作废时必须填写 void_reason
- 如果客户 credit_allowed=0，则 payment_type 不能为 'Crédito'

---

### 2.4 销售明细表（sale_item）

**用途**：存储销售单明细，每行代表一个规格的销售

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键 |
| sale_id | VARCHAR(50) | NOT NULL | 销售单号 |
| spec_id | INTEGER | NOT NULL | 规格ID |
| box_qty | INTEGER | NOT NULL DEFAULT 0 CHECK(box_qty >= 0) | 箱数 |
| extra_kg | DECIMAL(10,3) | NOT NULL DEFAULT 0 CHECK(extra_kg >= 0) | 散货重量（KG） |
| subtotal_kg | DECIMAL(12,3) | NOT NULL DEFAULT 0 | 小计重量（系统计算） |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**外键**：
- FOREIGN KEY (sale_id) REFERENCES sale(id)
- FOREIGN KEY (spec_id) REFERENCES spec(id)

**索引**：
- PRIMARY KEY (id)
- INDEX idx_sale_item_sale (sale_id)
- INDEX idx_sale_item_spec (spec_id)

**业务规则**：
- subtotal_kg = box_qty × spec.kg_per_box + extra_kg
- subtotal_kg 由系统自动计算，禁止人工修改
- box_qty 和 extra_kg 不能为负数
- 规格必须来自 spec 表，禁止自由输入

**计算公式**：
```sql
subtotal_kg = box_qty * (SELECT kg_per_box FROM spec WHERE id = spec_id) + extra_kg
```

---

### 2.5 库存变动表（stock_move）

**用途**：记录所有库存变动（进货、调拨、退货等），确保库存可追溯

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键 |
| move_type | VARCHAR(20) | NOT NULL CHECK(move_type IN ('进货','调拨','退货','盘盈','盘亏')) | 变动类型 |
| source | VARCHAR(100) | NOT NULL | 来源/去向，如：Granja El Castillo |
| kg | DECIMAL(12,3) | NOT NULL | 重量（正数为入库，负数为出库） |
| move_time | DATETIME | NOT NULL | 变动时间 |
| reference_id | VARCHAR(50) | NULL | 关联单据号（如销售单号） |
| reference_type | VARCHAR(20) | NULL | 关联单据类型（sale/purchase等） |
| notes | TEXT | NULL | 备注 |
| status | VARCHAR(20) | NOT NULL DEFAULT 'active' CHECK(status IN ('active','void')) | 状态 |
| void_reason | TEXT | NULL | 作废原因 |
| void_time | DATETIME | NULL | 作废时间 |
| void_by | VARCHAR(50) | NULL | 作废人 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| created_by | VARCHAR(50) | NOT NULL | 创建人 |

**索引**：
- PRIMARY KEY (id)
- INDEX idx_stock_move_time (move_time)
- INDEX idx_stock_move_type (move_type)
- INDEX idx_stock_move_status (status)
- INDEX idx_stock_move_reference (reference_type, reference_id)

**业务规则**：
- 进货、盘盈：kg > 0
- 调拨出库、退货、盘亏：kg < 0
- 销售出库通过触发器自动创建，reference_type='sale'
- 禁止物理删除，只能作废

**库存计算公式**：
```sql
当前库存 = SUM(kg) WHERE status='active'
```

---

### 2.6 审计日志表（audit_log）

**用途**：记录所有关键操作，确保对账可信性

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键 |
| table_name | VARCHAR(50) | NOT NULL | 表名 |
| record_id | VARCHAR(50) | NOT NULL | 记录ID |
| action | VARCHAR(20) | NOT NULL CHECK(action IN ('INSERT','UPDATE','DELETE','VOID')) | 操作类型 |
| old_value | TEXT | NULL | 修改前的值（JSON格式） |
| new_value | TEXT | NULL | 修改后的值（JSON格式） |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 操作时间 |
| created_by | VARCHAR(50) | NOT NULL | 操作人 |
| ip_address | VARCHAR(50) | NULL | IP地址 |

**索引**：
- PRIMARY KEY (id)
- INDEX idx_audit_table_record (table_name, record_id)
- INDEX idx_audit_created_at (created_at)
- INDEX idx_audit_created_by (created_by)

**业务规则**：
- 所有关键表的 INSERT/UPDATE/DELETE 操作都必须记录
- 日志表本身禁止修改和删除
- old_value 和 new_value 以 JSON 格式存储完整记录

---

### 2.7 盘点记录表（inventory_check）

**用途**：记录人工盘点结果，用于对账

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 主键 |
| check_time | DATETIME | NOT NULL | 盘点时间 |
| actual_kg | DECIMAL(12,3) | NOT NULL | 实际库存（KG） |
| theoretical_kg | DECIMAL(12,3) | NOT NULL | 理论库存（KG，系统计算） |
| difference_kg | DECIMAL(12,3) | NOT NULL | 差异（实际-理论） |
| notes | TEXT | NULL | 备注 |
| created_at | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| created_by | VARCHAR(50) | NOT NULL | 盘点人 |

**索引**：
- PRIMARY KEY (id)
- INDEX idx_inventory_check_time (check_time)

**业务规则**：
- theoretical_kg 由系统自动计算
- difference_kg = actual_kg - theoretical_kg
- 如果 |difference_kg| > 阈值，需要触发警告

---

## 三、触发器设计

### 3.1 销售明细自动计算 subtotal_kg

```sql
CREATE TRIGGER trg_sale_item_calc_subtotal
AFTER INSERT ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale_item
    SET subtotal_kg = NEW.box_qty * (SELECT kg_per_box FROM spec WHERE id = NEW.spec_id) + NEW.extra_kg
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_sale_item_update_subtotal
AFTER UPDATE OF box_qty, extra_kg, spec_id ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale_item
    SET subtotal_kg = NEW.box_qty * (SELECT kg_per_box FROM spec WHERE id = NEW.spec_id) + NEW.extra_kg
    WHERE id = NEW.id;
END;
```

### 3.2 销售单自动汇总 total_kg

```sql
CREATE TRIGGER trg_sale_calc_total
AFTER INSERT ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale
    SET total_kg = (SELECT IFNULL(SUM(subtotal_kg), 0) FROM sale_item WHERE sale_id = NEW.sale_id)
    WHERE id = NEW.sale_id;
END;

CREATE TRIGGER trg_sale_update_total
AFTER UPDATE ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale
    SET total_kg = (SELECT IFNULL(SUM(subtotal_kg), 0) FROM sale_item WHERE sale_id = NEW.sale_id)
    WHERE id = NEW.sale_id;
END;

CREATE TRIGGER trg_sale_delete_total
AFTER DELETE ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale
    SET total_kg = (SELECT IFNULL(SUM(subtotal_kg), 0) FROM sale_item WHERE sale_id = OLD.sale_id)
    WHERE id = OLD.sale_id;
END;
```

### 3.3 销售自动创建库存变动记录

```sql
CREATE TRIGGER trg_sale_create_stock_move
AFTER INSERT ON sale
FOR EACH ROW
WHEN NEW.status = 'active'
BEGIN
    INSERT INTO stock_move (move_type, source, kg, move_time, reference_id, reference_type, created_by)
    VALUES ('销售', (SELECT name FROM customer WHERE id = NEW.customer_id), -NEW.total_kg, NEW.sale_time, NEW.id, 'sale', NEW.created_by);
END;
```

### 3.4 销售作废时更新库存变动

```sql
CREATE TRIGGER trg_sale_void_stock_move
AFTER UPDATE OF status ON sale
FOR EACH ROW
WHEN NEW.status = 'void' AND OLD.status = 'active'
BEGIN
    UPDATE stock_move
    SET status = 'void', void_reason = NEW.void_reason, void_time = NEW.void_time, void_by = NEW.void_by
    WHERE reference_type = 'sale' AND reference_id = NEW.id;
END;
```

### 3.5 审计日志触发器

```sql
-- 销售单审计
CREATE TRIGGER trg_audit_sale_insert
AFTER INSERT ON sale
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, new_value, created_by)
    VALUES ('sale', NEW.id, 'INSERT', json_object('id', NEW.id, 'customer_id', NEW.customer_id, 'total_kg', NEW.total_kg), NEW.created_by);
END;

CREATE TRIGGER trg_audit_sale_update
AFTER UPDATE ON sale
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_value, new_value, created_by)
    VALUES ('sale', NEW.id, 'UPDATE', 
        json_object('status', OLD.status, 'total_kg', OLD.total_kg),
        json_object('status', NEW.status, 'total_kg', NEW.total_kg),
        NEW.updated_by);
END;
```

---

## 四、校验规则

### 4.1 数据库层面约束

1. **CHECK 约束**：
   - box_qty >= 0
   - extra_kg >= 0
   - kg_per_box > 0
   - payment_type IN ('现金','Crédito')
   - status IN ('active','void')

2. **FOREIGN KEY 约束**：
   - 确保 customer_id 存在
   - 确保 spec_id 存在

3. **UNIQUE 约束**：
   - spec.name 唯一
   - customer.name 唯一

### 4.2 应用层校验（需在后端实现）

1. **销售前校验**：
   - 如果 customer.credit_allowed=0，禁止使用 payment_type='Crédito'
   - 销售后库存不能为负数

2. **异常警告**：
   - 单箱重量偏差 > 10%：警告
   - 单笔重量 > 历史均值 2 倍：警告
   - extra_kg / total_kg > 30%：散货占比过高警告

3. **作废校验**：
   - 作废必须填写 void_reason
   - 作废后不能再修改

---

## 五、索引策略

### 5.1 查询优化索引

```sql
-- 按日期查询销售
CREATE INDEX idx_sale_time ON sale(sale_time);

-- 按客户统计
CREATE INDEX idx_sale_customer ON sale(customer_id);

-- 按规格统计
CREATE INDEX idx_sale_item_spec ON sale_item(spec_id);

-- 库存变动查询
CREATE INDEX idx_stock_move_time ON stock_move(move_time);
CREATE INDEX idx_stock_move_status ON stock_move(status);

-- 审计日志查询
CREATE INDEX idx_audit_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_table_record ON audit_log(table_name, record_id);
```

---

## 六、数据完整性保证

### 6.1 禁止操作

1. **禁止物理删除**：
   - sale 表禁止 DELETE
   - stock_move 表禁止 DELETE
   - 只能通过 status='void' 作废

2. **禁止人工修改计算字段**：
   - sale.total_kg
   - sale_item.subtotal_kg
   - inventory_check.theoretical_kg
   - inventory_check.difference_kg

3. **禁止自由输入**：
   - 规格必须来自 spec 表
   - 客户必须来自 customer 表

### 6.2 强制操作

1. **必须记录操作人**：
   - 所有表必须有 created_by
   - 修改操作必须有 updated_by
   - 作废操作必须有 void_by

2. **必须记录时间**：
   - 所有表必须有 created_at
   - 修改操作必须有 updated_at
   - 作废操作必须有 void_time

---

## 七、库存计算逻辑

### 7.1 理论库存计算

```sql
SELECT IFNULL(SUM(kg), 0) as theoretical_kg
FROM stock_move
WHERE status = 'active';
```

### 7.2 按日期计算库存

```sql
SELECT IFNULL(SUM(kg), 0) as stock_kg
FROM stock_move
WHERE status = 'active'
  AND move_time <= :target_date;
```

### 7.3 对账差异计算

```sql
SELECT 
    ic.check_time,
    ic.actual_kg,
    ic.theoretical_kg,
    ic.difference_kg,
    CASE 
        WHEN ABS(ic.difference_kg) > 50 THEN '严重差异'
        WHEN ABS(ic.difference_kg) > 20 THEN '需关注'
        ELSE '正常'
    END as status
FROM inventory_check ic
ORDER BY ic.check_time DESC;
```

---

## 八、统计查询示例

### 8.1 按日期统计销售

```sql
SELECT 
    DATE(sale_time) as sale_date,
    COUNT(*) as order_count,
    SUM(total_kg) as total_kg
FROM sale
WHERE status = 'active'
  AND sale_time >= :start_date
  AND sale_time <= :end_date
GROUP BY DATE(sale_time)
ORDER BY sale_date;
```

### 8.2 按客户统计

```sql
SELECT 
    c.name as customer_name,
    COUNT(s.id) as order_count,
    SUM(s.total_kg) as total_kg
FROM sale s
JOIN customer c ON s.customer_id = c.id
WHERE s.status = 'active'
  AND s.sale_time >= :start_date
  AND s.sale_time <= :end_date
GROUP BY c.id, c.name
ORDER BY total_kg DESC;
```

### 8.3 按规格统计

```sql
SELECT 
    sp.name as spec_name,
    SUM(si.box_qty) as total_boxes,
    SUM(si.extra_kg) as total_extra_kg,
    SUM(si.subtotal_kg) as total_kg
FROM sale_item si
JOIN spec sp ON si.spec_id = sp.id
JOIN sale s ON si.sale_id = s.id
WHERE s.status = 'active'
  AND s.sale_time >= :start_date
  AND s.sale_time <= :end_date
GROUP BY sp.id, sp.name
ORDER BY total_kg DESC;
```

### 8.4 散货占比统计

```sql
SELECT 
    s.id,
    s.sale_time,
    s.total_kg,
    SUM(si.extra_kg) as extra_kg,
    ROUND(SUM(si.extra_kg) * 100.0 / s.total_kg, 2) as extra_percent
FROM sale s
JOIN sale_item si ON s.id = si.sale_id
WHERE s.status = 'active'
GROUP BY s.id
HAVING extra_percent > 30
ORDER BY extra_percent DESC;
```

---

## 九、数据迁移说明

### 9.1 从 Excel 导入数据

根据 table01.jpg 中的数据结构，需要进行以下映射：

| Excel 列 | 数据库表.字段 | 处理逻辑 |
|----------|---------------|----------|
| Fecha | sale.sale_time | 直接映射 |
| Usuario | sale.created_by | 直接映射 |
| ID | sale.id | 直接映射 |
| Tipo | - | 固定为"Venta"，不存储 |
| Categoría | - | 固定为"Sin categoría"，不存储 |
| Método de pago | - | 固定为"Otro"，不存储 |
| Tipo de pago | sale.payment_type | 映射为"现金"或"Crédito" |
| Descripción | - | **需要解析为规格** |
| Productos | - | 从描述中提取 |
| Contacto | customer.name | 创建客户记录 |

### 9.2 描述字段解析规则

Excel 中的 Descripción 字段包含自由文本，需要解析为规格：

**示例**：
- "20 KG X 110" → spec: "JAVA 20x110", box_qty: 1
- "2 JAVAS DE 39X110" → spec: "JAVA 39x110", box_qty: 2
- "3 JAVAS DE 39X110 + 2 JAVAS DE 38X115" → 需要拆分为 2 条 sale_item

**解析步骤**：
1. 提取所有规格信息
2. 在 spec 表中查找或创建规格
3. 创建对应的 sale_item 记录
4. 系统自动计算 subtotal_kg 和 total_kg

---

## 十、备份与恢复策略

### 10.1 备份策略

1. **每日自动备份**：
   - 完整数据库备份
   - 保留最近 30 天

2. **关键操作前备份**：
   - 批量导入前
   - 系统升级前

3. **审计日志归档**：
   - 每月归档一次
   - 永久保留

### 10.2 恢复测试

- 每月进行一次恢复测试
- 确保备份可用性

---

## 十一、性能优化建议

### 11.1 查询优化

1. 使用索引覆盖常用查询
2. 避免全表扫描
3. 使用分页查询

### 11.2 数据归档

1. 超过 1 年的销售数据归档
2. 审计日志定期归档
3. 保留汇总统计数据

---

## 十二、安全性设计

### 12.1 数据访问控制

1. **操作员权限**：
   - 只能创建销售单
   - 不能作废销售单
   - 不能修改规格

2. **管理员权限**：
   - 可以作废销售单
   - 可以维护规格
   - 可以查看审计日志

### 12.2 数据加密

1. 敏感字段加密（如有需要）
2. 通信加密（HTTPS）
3. 数据库连接加密

---

## 十三、监控与告警

### 13.1 实时监控

1. 库存异常：库存 < 0
2. 差异过大：盘点差异 > 阈值
3. 异常订单：单笔重量 > 历史均值 2 倍

### 13.2 定期报告

1. 每日库存报告
2. 每周销售汇总
3. 每月对账报告

---

## 十四、版本控制

| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| 1.0 | 2026-01-05 | 初始版本 | Claude |

---

## 十五、附录

### 15.1 数据字典

详见各表结构说明。

### 15.2 ER 图

```
customer ──┐
           │
           ├──< sale >──< sale_item >──┤
           │                           │
           │                         spec
           │
           └──< stock_move
```

### 15.3 业务流程图

```
开始 → 选择客户 → 选择支付方式 → 添加明细 → 系统计算重量 → 校验 → 保存 → 自动创建库存变动 → 结束
```

---

**文档结束**
