-- ============================================================================
-- 数据库初始化脚本
-- 项目：销售管理系统
-- 版本：1.0
-- 日期：2026-01-05
-- 说明：严格按照开发文档实现，禁止自由规格输入，重量由系统计算，库存可追溯
-- ============================================================================

-- ============================================================================
-- 1. 规格表（spec）
-- 用途：存储所有产品规格，禁止自由输入规格文本
-- ============================================================================
CREATE TABLE IF NOT EXISTS spec (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,              -- 规格名称，如：JAVA 39x110
    length INTEGER NOT NULL,                         -- 长度（cm）
    width INTEGER NOT NULL,                          -- 宽度（cm）
    kg_per_box DECIMAL(10,3) NOT NULL CHECK(kg_per_box > 0),  -- 单箱标准重量（KG）
    active BOOLEAN NOT NULL DEFAULT 1,               -- 是否启用
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    updated_at DATETIME NULL,
    updated_by VARCHAR(50) NULL
);

-- 索引
CREATE UNIQUE INDEX idx_spec_name ON spec(name);
CREATE INDEX idx_spec_active ON spec(active);

-- ============================================================================
-- 2. 客户表（customer）
-- 用途：存储客户信息
-- ============================================================================
CREATE TABLE IF NOT EXISTS customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,               -- 客户名称
    credit_allowed BOOLEAN NOT NULL DEFAULT 0,       -- 是否允许信用支付
    active BOOLEAN NOT NULL DEFAULT 1,               -- 是否启用
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    updated_at DATETIME NULL,
    updated_by VARCHAR(50) NULL
);

-- 索引
CREATE UNIQUE INDEX idx_customer_name ON customer(name);
CREATE INDEX idx_customer_active ON customer(active);

-- ============================================================================
-- 3. 销售单主表（sale）
-- 用途：存储销售单主信息
-- 业务规则：
--   1. total_kg 由系统自动计算，禁止人工修改
--   2. 销售单禁止物理删除，只能作废（status='void'）
--   3. 作废时必须填写 void_reason
-- ============================================================================
CREATE TABLE IF NOT EXISTS sale (
    id VARCHAR(50) PRIMARY KEY,                      -- 单据号，格式：SALE-YYYYMMDD-序号
    sale_time DATETIME NOT NULL,                     -- 销售时间
    customer_id INTEGER NOT NULL,                    -- 客户ID
    payment_type VARCHAR(20) NOT NULL CHECK(payment_type IN ('现金','Crédito')),  -- 支付方式
    total_kg DECIMAL(12,3) NOT NULL DEFAULT 0,       -- 总重量（自动汇总，禁止人工输入）
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK(status IN ('active','void')),  -- 状态
    void_reason TEXT NULL,                           -- 作废原因
    void_time DATETIME NULL,                         -- 作废时间
    void_by VARCHAR(50) NULL,                        -- 作废人
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,                 -- 创建人（操作员）
    updated_at DATETIME NULL,
    updated_by VARCHAR(50) NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(id)
);

-- 索引
CREATE INDEX idx_sale_time ON sale(sale_time);
CREATE INDEX idx_sale_customer ON sale(customer_id);
CREATE INDEX idx_sale_status ON sale(status);
CREATE INDEX idx_sale_created_by ON sale(created_by);

-- ============================================================================
-- 4. 销售明细表（sale_item）
-- 用途：存储销售单明细，每行代表一个规格的销售
-- 业务规则：
--   1. subtotal_kg = box_qty × spec.kg_per_box + extra_kg
--   2. subtotal_kg 由系统自动计算，禁止人工修改
--   3. 规格必须来自 spec 表，禁止自由输入
-- ============================================================================
CREATE TABLE IF NOT EXISTS sale_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id VARCHAR(50) NOT NULL,                    -- 销售单号
    spec_id INTEGER NOT NULL,                        -- 规格ID
    box_qty INTEGER NOT NULL DEFAULT 0 CHECK(box_qty >= 0),  -- 箱数
    extra_kg DECIMAL(10,3) NOT NULL DEFAULT 0 CHECK(extra_kg >= 0),  -- 散货重量（KG）
    subtotal_kg DECIMAL(12,3) NOT NULL DEFAULT 0,    -- 小计重量（系统计算）
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sale(id),
    FOREIGN KEY (spec_id) REFERENCES spec(id)
);

-- 索引
CREATE INDEX idx_sale_item_sale ON sale_item(sale_id);
CREATE INDEX idx_sale_item_spec ON sale_item(spec_id);

-- ============================================================================
-- 5. 库存变动表（stock_move）
-- 用途：记录所有库存变动（进货、调拨、退货等），确保库存可追溯
-- 业务规则：
--   1. 进货、盘盈：kg > 0
--   2. 调拨出库、退货、盘亏、销售：kg < 0
--   3. 销售出库通过触发器自动创建
--   4. 禁止物理删除，只能作废
-- ============================================================================
CREATE TABLE IF NOT EXISTS stock_move (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    move_type VARCHAR(20) NOT NULL CHECK(move_type IN ('进货','调拨','退货','盘盈','盘亏','销售')),
    source VARCHAR(100) NOT NULL,                    -- 来源/去向
    kg DECIMAL(12,3) NOT NULL,                       -- 重量（正数为入库，负数为出库）
    move_time DATETIME NOT NULL,                     -- 变动时间
    reference_id VARCHAR(50) NULL,                   -- 关联单据号
    reference_type VARCHAR(20) NULL,                 -- 关联单据类型
    notes TEXT NULL,                                 -- 备注
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK(status IN ('active','void')),
    void_reason TEXT NULL,                           -- 作废原因
    void_time DATETIME NULL,                         -- 作废时间
    void_by VARCHAR(50) NULL,                        -- 作废人
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL
);

-- 索引
CREATE INDEX idx_stock_move_time ON stock_move(move_time);
CREATE INDEX idx_stock_move_type ON stock_move(move_type);
CREATE INDEX idx_stock_move_status ON stock_move(status);
CREATE INDEX idx_stock_move_reference ON stock_move(reference_type, reference_id);

-- ============================================================================
-- 6. 审计日志表（audit_log）
-- 用途：记录所有关键操作，确保对账可信性
-- 业务规则：
--   1. 所有关键表的 INSERT/UPDATE/DELETE 操作都必须记录
--   2. 日志表本身禁止修改和删除
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name VARCHAR(50) NOT NULL,                 -- 表名
    record_id VARCHAR(50) NOT NULL,                  -- 记录ID
    action VARCHAR(20) NOT NULL CHECK(action IN ('INSERT','UPDATE','DELETE','VOID')),
    old_value TEXT NULL,                             -- 修改前的值（JSON格式）
    new_value TEXT NULL,                             -- 修改后的值（JSON格式）
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50) NULL
);

-- 索引
CREATE INDEX idx_audit_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_created_by ON audit_log(created_by);

-- ============================================================================
-- 7. 盘点记录表（inventory_check）
-- 用途：记录人工盘点结果，用于对账
-- 业务规则：
--   1. theoretical_kg 由系统自动计算
--   2. difference_kg = actual_kg - theoretical_kg
-- ============================================================================
CREATE TABLE IF NOT EXISTS inventory_check (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_time DATETIME NOT NULL,                    -- 盘点时间
    actual_kg DECIMAL(12,3) NOT NULL,                -- 实际库存（KG）
    theoretical_kg DECIMAL(12,3) NOT NULL,           -- 理论库存（KG，系统计算）
    difference_kg DECIMAL(12,3) NOT NULL,            -- 差异（实际-理论）
    notes TEXT NULL,                                 -- 备注
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL                  -- 盘点人
);

-- 索引
CREATE INDEX idx_inventory_check_time ON inventory_check(check_time);

-- ============================================================================
-- 8. 备忘录表（memo）
-- 用途：系统设置页面简单的备忘录/待办事项
-- ============================================================================
CREATE TABLE IF NOT EXISTS memo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,                           -- 内容
    memo_date DATE NOT NULL,                         -- 日期
    is_completed BOOLEAN NOT NULL DEFAULT 0,         -- 是否完成
    active BOOLEAN NOT NULL DEFAULT 1,               -- 是否启用（软删除）
    reference_type VARCHAR(20) NULL,                 -- 关联类型: 'sale' 或 'purchase'
    reference_id VARCHAR(50) NULL,                   -- 关联记录ID
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    updated_at DATETIME NULL,
    updated_by VARCHAR(50) NULL
);

-- 索引
CREATE INDEX idx_memo_date ON memo(memo_date);
CREATE INDEX idx_memo_active ON memo(active);
CREATE INDEX idx_memo_created_at ON memo(created_at);

-- ============================================================================
-- 触发器部分
-- ============================================================================

-- ============================================================================
-- 触发器 1：销售明细自动计算 subtotal_kg（INSERT）
-- ============================================================================
CREATE TRIGGER trg_sale_item_calc_subtotal_insert
AFTER INSERT ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale_item
    SET subtotal_kg = NEW.box_qty * (SELECT kg_per_box FROM spec WHERE id = NEW.spec_id) + NEW.extra_kg
    WHERE id = NEW.id;
END;

-- ============================================================================
-- 触发器 2：销售明细自动计算 subtotal_kg（UPDATE）
-- ============================================================================
CREATE TRIGGER trg_sale_item_calc_subtotal_update
AFTER UPDATE OF box_qty, extra_kg, spec_id ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale_item
    SET subtotal_kg = NEW.box_qty * (SELECT kg_per_box FROM spec WHERE id = NEW.spec_id) + NEW.extra_kg
    WHERE id = NEW.id;
END;

-- ============================================================================
-- 触发器 3：销售单自动汇总 total_kg（INSERT sale_item）
-- ============================================================================
CREATE TRIGGER trg_sale_calc_total_insert
AFTER INSERT ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale
    SET total_kg = (SELECT IFNULL(SUM(subtotal_kg), 0) FROM sale_item WHERE sale_id = NEW.sale_id)
    WHERE id = NEW.sale_id;
END;

-- ============================================================================
-- 触发器 4：销售单自动汇总 total_kg（UPDATE sale_item）
-- ============================================================================
CREATE TRIGGER trg_sale_calc_total_update
AFTER UPDATE ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale
    SET total_kg = (SELECT IFNULL(SUM(subtotal_kg), 0) FROM sale_item WHERE sale_id = NEW.sale_id)
    WHERE id = NEW.sale_id;
END;

-- ============================================================================
-- 触发器 5：销售单自动汇总 total_kg（DELETE sale_item）
-- ============================================================================
CREATE TRIGGER trg_sale_calc_total_delete
AFTER DELETE ON sale_item
FOR EACH ROW
BEGIN
    UPDATE sale
    SET total_kg = (SELECT IFNULL(SUM(subtotal_kg), 0) FROM sale_item WHERE sale_id = OLD.sale_id)
    WHERE id = OLD.sale_id;
END;

-- ============================================================================
-- 触发器 6：销售自动创建库存变动记录
-- ============================================================================
CREATE TRIGGER trg_sale_create_stock_move
AFTER UPDATE OF total_kg ON sale
FOR EACH ROW
WHEN NEW.status = 'active' AND NEW.total_kg > 0
    AND NOT EXISTS (SELECT 1 FROM stock_move WHERE reference_type = 'sale' AND reference_id = NEW.id AND status = 'active')
BEGIN
    INSERT INTO stock_move (move_type, source, kg, move_time, reference_id, reference_type, created_by)
    VALUES ('销售', (SELECT name FROM customer WHERE id = NEW.customer_id), -NEW.total_kg, NEW.sale_time, NEW.id, 'sale', NEW.created_by);
END;

-- ============================================================================
-- 触发器 7：销售作废时更新库存变动
-- ============================================================================
CREATE TRIGGER trg_sale_void_stock_move
AFTER UPDATE OF status ON sale
FOR EACH ROW
WHEN NEW.status = 'void' AND OLD.status = 'active'
BEGIN
    UPDATE stock_move
    SET status = 'void', void_reason = NEW.void_reason, void_time = NEW.void_time, void_by = NEW.void_by
    WHERE reference_type = 'sale' AND reference_id = NEW.id;
END;

-- ============================================================================
-- 触发器 8：销售单审计日志（INSERT）
-- ============================================================================
CREATE TRIGGER trg_audit_sale_insert
AFTER INSERT ON sale
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, new_value, created_by)
    VALUES ('sale', NEW.id, 'INSERT', 
        json_object('id', NEW.id, 'customer_id', NEW.customer_id, 'payment_type', NEW.payment_type, 'total_kg', NEW.total_kg, 'status', NEW.status),
        NEW.created_by);
END;

-- ============================================================================
-- 触发器 9：销售单审计日志（UPDATE）
-- ============================================================================
CREATE TRIGGER trg_audit_sale_update
AFTER UPDATE ON sale
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_value, new_value, created_by)
    VALUES ('sale', NEW.id, 'UPDATE', 
        json_object('status', OLD.status, 'total_kg', OLD.total_kg, 'payment_type', OLD.payment_type),
        json_object('status', NEW.status, 'total_kg', NEW.total_kg, 'payment_type', NEW.payment_type),
        COALESCE(NEW.updated_by, NEW.created_by));
END;

-- ============================================================================
-- 触发器 10：规格表审计日志（INSERT）
-- ============================================================================
CREATE TRIGGER trg_audit_spec_insert
AFTER INSERT ON spec
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, new_value, created_by)
    VALUES ('spec', CAST(NEW.id AS TEXT), 'INSERT',
        json_object('name', NEW.name, 'length', NEW.length, 'width', NEW.width, 'kg_per_box', NEW.kg_per_box, 'active', NEW.active),
        NEW.created_by);
END;

-- ============================================================================
-- 触发器 11：规格表审计日志（UPDATE）
-- ============================================================================
CREATE TRIGGER trg_audit_spec_update
AFTER UPDATE ON spec
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_value, new_value, created_by)
    VALUES ('spec', CAST(NEW.id AS TEXT), 'UPDATE',
        json_object('name', OLD.name, 'kg_per_box', OLD.kg_per_box, 'active', OLD.active),
        json_object('name', NEW.name, 'kg_per_box', NEW.kg_per_box, 'active', NEW.active),
        COALESCE(NEW.updated_by, NEW.created_by));
END;

-- ============================================================================
-- 触发器 12：库存变动审计日志（INSERT）
-- ============================================================================
CREATE TRIGGER trg_audit_stock_move_insert
AFTER INSERT ON stock_move
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, new_value, created_by)
    VALUES ('stock_move', CAST(NEW.id AS TEXT), 'INSERT',
        json_object('move_type', NEW.move_type, 'source', NEW.source, 'kg', NEW.kg, 'move_time', NEW.move_time, 'reference_id', NEW.reference_id),
        NEW.created_by);
END;

-- ============================================================================
-- 触发器 13：库存变动审计日志（UPDATE）
-- ============================================================================
CREATE TRIGGER trg_audit_stock_move_update
AFTER UPDATE ON stock_move
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_value, new_value, created_by)
    VALUES ('stock_move', CAST(NEW.id AS TEXT), 'UPDATE',
        json_object('status', OLD.status, 'kg', OLD.kg),
        json_object('status', NEW.status, 'kg', NEW.kg),
        COALESCE(NEW.void_by, NEW.created_by));
END;

-- ============================================================================
-- 初始数据插入
-- ============================================================================

-- 插入默认管理员用户（用于 created_by）
-- 注意：实际应用中应该有独立的用户表

-- 插入常用规格示例（根据 table01.jpg 中的数据）
INSERT INTO spec (name, length, width, kg_per_box, active, created_by) VALUES
('JAVA 39x110', 39, 110, 20, 1, 'system'),
('JAVA 38x104', 38, 104, 15, 1, 'system'),
('JAVA 38x110', 38, 110, 15, 1, 'system'),
('JAVA 38x115', 38, 115, 15, 1, 'system'),
('JAVA 40x115', 40, 115, 15, 1, 'system'),
('JAVA 39x115', 39, 115, 15, 1, 'system'),
('JAVA 39x105', 39, 105, 15, 1, 'system'),
('JAVA 36x96', 36, 96, 10, 1, 'system'),
('JAVA 36x100', 36, 100, 10, 1, 'system'),
('JAVA 36x104', 36, 104, 10, 1, 'system'),
('JAVA 36x105', 36, 105, 10, 1, 'system'),
('JAVA 36x110', 36, 110, 10, 1, 'system'),
('JAVA 36x120', 36, 120, 10, 1, 'system'),
('JAVA 40x120', 40, 120, 15, 1, 'system');

-- 插入常用客户示例（根据 table01.jpg 中的数据）
INSERT INTO customer (name, credit_allowed, active, created_by) VALUES
('DANIEL HIELO', 1, 1, 'system'),
('doña lety', 1, 1, 'system'),
('CARLOS YESSENIA', 1, 1, 'system'),
('sujeil juarez', 1, 1, 'system'),
('lizardo burgueno', 1, 1, 'system'),
('hermano ramon', 1, 1, 'system'),
('david', 1, 1, 'system'),
('Chaya juarez', 1, 1, 'system'),
('fernando 82', 1, 1, 'system'),
('laurita cerdan', 1, 1, 'system'),
('niña mercado', 1, 1, 'system'),
('paloma maz', 1, 1, 'system'),
('Rosario cerdan', 1, 1, 'system'),
('karla', 1, 1, 'system'),
('Ana fer', 1, 1, 'system'),
('linda juarez', 1, 1, 'system'),
('fernanda 2', 1, 1, 'system'),
('Cipriano', 1, 1, 'system'),
('marlen cerdan', 1, 1, 'system'),
('guero reynosa', 1, 1, 'system'),
('diego cubetero', 1, 1, 'system'),
('granja el castillo', 1, 1, 'system');

-- ============================================================================
-- 常用查询视图
-- ============================================================================

-- 视图 1：当前库存
CREATE VIEW IF NOT EXISTS v_current_stock AS
SELECT 
    IFNULL(SUM(kg), 0) as current_stock_kg,
    COUNT(*) as total_moves,
    MAX(move_time) as last_move_time
FROM stock_move
WHERE status = 'active';

-- 视图 2：今日销售汇总
CREATE VIEW IF NOT EXISTS v_today_sales AS
SELECT 
    DATE(sale_time) as sale_date,
    COUNT(*) as order_count,
    SUM(total_kg) as total_kg,
    SUM(CASE WHEN payment_type = '现金' THEN total_kg ELSE 0 END) as cash_kg,
    SUM(CASE WHEN payment_type = 'Crédito' THEN total_kg ELSE 0 END) as credit_kg
FROM sale
WHERE status = 'active'
  AND DATE(sale_time) = DATE('now')
GROUP BY DATE(sale_time);

-- 视图 3：客户销售排名
CREATE VIEW IF NOT EXISTS v_customer_ranking AS
SELECT 
    c.id,
    c.name as customer_name,
    COUNT(s.id) as order_count,
    SUM(s.total_kg) as total_kg,
    MAX(s.sale_time) as last_sale_time
FROM customer c
LEFT JOIN sale s ON c.id = s.customer_id AND s.status = 'active'
GROUP BY c.id, c.name
ORDER BY total_kg DESC;

-- 视图 4：规格使用统计
CREATE VIEW IF NOT EXISTS v_spec_usage AS
SELECT 
    sp.id,
    sp.name as spec_name,
    sp.kg_per_box,
    COUNT(si.id) as usage_count,
    SUM(si.box_qty) as total_boxes,
    SUM(si.extra_kg) as total_extra_kg,
    SUM(si.subtotal_kg) as total_kg
FROM spec sp
LEFT JOIN sale_item si ON sp.id = si.spec_id
LEFT JOIN sale s ON si.sale_id = s.id AND s.status = 'active'
GROUP BY sp.id, sp.name, sp.kg_per_box
ORDER BY total_kg DESC;

-- 视图 5：散货占比分析
CREATE VIEW IF NOT EXISTS v_extra_kg_analysis AS
SELECT 
    s.id as sale_id,
    s.sale_time,
    c.name as customer_name,
    s.total_kg,
    SUM(si.extra_kg) as extra_kg,
    ROUND(SUM(si.extra_kg) * 100.0 / NULLIF(s.total_kg, 0), 2) as extra_percent
FROM sale s
JOIN customer c ON s.customer_id = c.id
JOIN sale_item si ON s.id = si.sale_id
WHERE s.status = 'active'
GROUP BY s.id, s.sale_time, c.name, s.total_kg
HAVING extra_percent > 0
ORDER BY extra_percent DESC;

-- ============================================================================
-- 脚本结束
-- ============================================================================

-- 验证表创建
SELECT 'Tables created successfully!' as status;
SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;
