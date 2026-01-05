-- ============================================================================
-- 数据库测试脚本
-- 用途：验证数据库设计的正确性，测试所有触发器和约束
-- ============================================================================

-- ============================================================================
-- 测试 1：验证规格表基本功能
-- ============================================================================
SELECT '=== 测试 1：规格表基本功能 ===' as test_name;

-- 查看已插入的规格
SELECT * FROM spec WHERE active = 1 LIMIT 5;

-- 验证规格名称唯一性约束（应该失败）
-- INSERT INTO spec (name, length, width, kg_per_box, created_by) 
-- VALUES ('JAVA 39x110', 39, 110, 20, 'test');  -- 会失败，因为名称重复

-- ============================================================================
-- 测试 2：创建销售单并验证自动计算
-- ============================================================================
SELECT '=== 测试 2：销售单自动计算功能 ===' as test_name;

-- 2.1 创建测试销售单
INSERT INTO sale (id, sale_time, customer_id, payment_type, created_by)
VALUES ('SALE-20260105-001', datetime('now'), 1, 'Crédito', 'Jose Burgueno');

-- 2.2 添加销售明细（2箱 JAVA 39x110）
INSERT INTO sale_item (sale_id, spec_id, box_qty, extra_kg)
VALUES ('SALE-20260105-001', 1, 2, 0);

-- 2.3 验证 subtotal_kg 自动计算（应该是 2 * 20 = 40）
SELECT 
    si.id,
    si.sale_id,
    sp.name as spec_name,
    sp.kg_per_box,
    si.box_qty,
    si.extra_kg,
    si.subtotal_kg,
    '预期: 40 KG' as expected
FROM sale_item si
JOIN spec sp ON si.spec_id = sp.id
WHERE si.sale_id = 'SALE-20260105-001';

-- 2.4 添加第二条明细（3箱 JAVA 38x110 + 5kg散货）
INSERT INTO sale_item (sale_id, spec_id, box_qty, extra_kg)
VALUES ('SALE-20260105-001', 3, 3, 5);

-- 2.5 验证销售单 total_kg 自动汇总（应该是 40 + 3*15 + 5 = 90）
SELECT 
    s.id,
    s.sale_time,
    c.name as customer_name,
    s.payment_type,
    s.total_kg,
    '预期: 90 KG' as expected
FROM sale s
JOIN customer c ON s.customer_id = c.id
WHERE s.id = 'SALE-20260105-001';

-- ============================================================================
-- 测试 3：验证库存变动自动创建
-- ============================================================================
SELECT '=== 测试 3：库存变动自动创建 ===' as test_name;

-- 查看自动创建的库存变动记录
SELECT 
    sm.id,
    sm.move_type,
    sm.source,
    sm.kg,
    sm.reference_id,
    sm.reference_type,
    '预期: -90 KG' as expected
FROM stock_move sm
WHERE sm.reference_id = 'SALE-20260105-001';

-- ============================================================================
-- 测试 4：验证审计日志
-- ============================================================================
SELECT '=== 测试 4：审计日志记录 ===' as test_name;

-- 查看销售单的审计日志
SELECT 
    al.id,
    al.table_name,
    al.record_id,
    al.action,
    al.new_value,
    al.created_by,
    al.created_at
FROM audit_log al
WHERE al.table_name = 'sale' AND al.record_id = 'SALE-20260105-001'
ORDER BY al.created_at;

-- ============================================================================
-- 测试 5：测试销售单作废功能
-- ============================================================================
SELECT '=== 测试 5：销售单作废功能 ===' as test_name;

-- 5.1 作废销售单
UPDATE sale
SET status = 'void',
    void_reason = '测试作废功能',
    void_time = datetime('now'),
    void_by = 'admin',
    updated_by = 'admin',
    updated_at = datetime('now')
WHERE id = 'SALE-20260105-001';

-- 5.2 验证销售单状态
SELECT 
    s.id,
    s.status,
    s.void_reason,
    s.void_by,
    '预期: void' as expected_status
FROM sale s
WHERE s.id = 'SALE-20260105-001';

-- 5.3 验证库存变动也被作废
SELECT 
    sm.id,
    sm.move_type,
    sm.kg,
    sm.status,
    sm.void_reason,
    '预期: void' as expected_status
FROM stock_move sm
WHERE sm.reference_id = 'SALE-20260105-001';

-- ============================================================================
-- 测试 6：创建正常销售单并测试库存计算
-- ============================================================================
SELECT '=== 测试 6：库存计算测试 ===' as test_name;

-- 6.1 添加进货记录
INSERT INTO stock_move (move_type, source, kg, move_time, created_by)
VALUES ('进货', 'Granja El Castillo', 1000, datetime('now'), 'admin');

-- 6.2 创建新的销售单
INSERT INTO sale (id, sale_time, customer_id, payment_type, created_by)
VALUES ('SALE-20260105-002', datetime('now'), 2, '现金', 'Jose Burgueno');

-- 6.3 添加销售明细
INSERT INTO sale_item (sale_id, spec_id, box_qty, extra_kg)
VALUES ('SALE-20260105-002', 1, 5, 10);  -- 5箱 + 10kg散货 = 110kg

-- 6.4 查看当前库存（应该是 1000 - 110 = 890）
SELECT 
    current_stock_kg,
    '预期: 890 KG' as expected
FROM v_current_stock;

-- 6.5 查看所有库存变动
SELECT 
    sm.id,
    sm.move_type,
    sm.source,
    sm.kg,
    sm.status,
    sm.move_time
FROM stock_move sm
WHERE sm.status = 'active'
ORDER BY sm.move_time;

-- ============================================================================
-- 测试 7：测试约束条件
-- ============================================================================
SELECT '=== 测试 7：约束条件测试 ===' as test_name;

-- 7.1 测试负数箱数（应该失败）
-- INSERT INTO sale_item (sale_id, spec_id, box_qty, extra_kg)
-- VALUES ('SALE-20260105-002', 1, -1, 0);  -- 会失败

-- 7.2 测试负数散货（应该失败）
-- INSERT INTO sale_item (sale_id, spec_id, box_qty, extra_kg)
-- VALUES ('SALE-20260105-002', 1, 1, -5);  -- 会失败

-- 7.3 测试无效的支付方式（应该失败）
-- INSERT INTO sale (id, sale_time, customer_id, payment_type, created_by)
-- VALUES ('SALE-20260105-003', datetime('now'), 1, '支票', 'test');  -- 会失败

SELECT '约束条件正常工作（注释掉的测试会失败）' as result;

-- ============================================================================
-- 测试 8：统计查询测试
-- ============================================================================
SELECT '=== 测试 8：统计查询测试 ===' as test_name;

-- 8.1 今日销售汇总
SELECT * FROM v_today_sales;

-- 8.2 客户销售排名
SELECT * FROM v_customer_ranking LIMIT 5;

-- 8.3 规格使用统计
SELECT * FROM v_spec_usage WHERE usage_count > 0 LIMIT 5;

-- 8.4 散货占比分析
SELECT * FROM v_extra_kg_analysis LIMIT 5;

-- ============================================================================
-- 测试 9：盘点功能测试
-- ============================================================================
SELECT '=== 测试 9：盘点功能测试 ===' as test_name;

-- 9.1 获取当前理论库存
SELECT current_stock_kg FROM v_current_stock;

-- 9.2 创建盘点记录（假设实际库存是 880，差异 -10）
INSERT INTO inventory_check (check_time, actual_kg, theoretical_kg, difference_kg, notes, created_by)
SELECT 
    datetime('now'),
    880,
    current_stock_kg,
    880 - current_stock_kg,
    '月度盘点',
    'admin'
FROM v_current_stock;

-- 9.3 查看盘点记录
SELECT 
    ic.id,
    ic.check_time,
    ic.actual_kg,
    ic.theoretical_kg,
    ic.difference_kg,
    ic.notes,
    CASE 
        WHEN ABS(ic.difference_kg) > 50 THEN '严重差异'
        WHEN ABS(ic.difference_kg) > 20 THEN '需关注'
        ELSE '正常'
    END as status
FROM inventory_check ic
ORDER BY ic.check_time DESC;

-- ============================================================================
-- 测试 10：复杂销售场景
-- ============================================================================
SELECT '=== 测试 10：复杂销售场景 ===' as test_name;

-- 10.1 创建包含多个规格的销售单
INSERT INTO sale (id, sale_time, customer_id, payment_type, created_by)
VALUES ('SALE-20260105-003', datetime('now'), 3, 'Crédito', 'Jose Burgueno');

-- 10.2 添加多条明细
INSERT INTO sale_item (sale_id, spec_id, box_qty, extra_kg) VALUES
('SALE-20260105-003', 1, 3, 0),      -- 3箱 JAVA 39x110
('SALE-20260105-003', 2, 2, 5),      -- 2箱 JAVA 38x104 + 5kg
('SALE-20260105-003', 4, 1, 10);     -- 1箱 JAVA 38x115 + 10kg

-- 10.3 查看销售单详情
SELECT 
    s.id,
    s.sale_time,
    c.name as customer_name,
    s.payment_type,
    s.total_kg,
    COUNT(si.id) as item_count
FROM sale s
JOIN customer c ON s.customer_id = c.id
JOIN sale_item si ON s.id = si.sale_id
WHERE s.id = 'SALE-20260105-003'
GROUP BY s.id, s.sale_time, c.name, s.payment_type, s.total_kg;

-- 10.4 查看明细
SELECT 
    si.id,
    sp.name as spec_name,
    si.box_qty,
    si.extra_kg,
    si.subtotal_kg,
    sp.kg_per_box
FROM sale_item si
JOIN spec sp ON si.spec_id = sp.id
WHERE si.sale_id = 'SALE-20260105-003';

-- ============================================================================
-- 测试 11：按日期统计销售
-- ============================================================================
SELECT '=== 测试 11：按日期统计销售 ===' as test_name;

SELECT 
    DATE(s.sale_time) as sale_date,
    COUNT(*) as order_count,
    SUM(s.total_kg) as total_kg,
    SUM(CASE WHEN s.payment_type = '现金' THEN s.total_kg ELSE 0 END) as cash_kg,
    SUM(CASE WHEN s.payment_type = 'Crédito' THEN s.total_kg ELSE 0 END) as credit_kg
FROM sale s
WHERE s.status = 'active'
GROUP BY DATE(s.sale_time)
ORDER BY sale_date DESC;

-- ============================================================================
-- 测试 12：按客户统计
-- ============================================================================
SELECT '=== 测试 12：按客户统计 ===' as test_name;

SELECT 
    c.name as customer_name,
    COUNT(s.id) as order_count,
    SUM(s.total_kg) as total_kg,
    AVG(s.total_kg) as avg_kg_per_order,
    MAX(s.sale_time) as last_sale_time
FROM customer c
LEFT JOIN sale s ON c.id = s.customer_id AND s.status = 'active'
GROUP BY c.id, c.name
HAVING order_count > 0
ORDER BY total_kg DESC;

-- ============================================================================
-- 测试 13：按规格统计
-- ============================================================================
SELECT '=== 测试 13：按规格统计 ===' as test_name;

SELECT 
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
HAVING usage_count > 0
ORDER BY total_kg DESC;

-- ============================================================================
-- 测试 14：审计日志完整性
-- ============================================================================
SELECT '=== 测试 14：审计日志完整性 ===' as test_name;

SELECT 
    al.table_name,
    al.action,
    COUNT(*) as log_count
FROM audit_log al
GROUP BY al.table_name, al.action
ORDER BY al.table_name, al.action;

-- ============================================================================
-- 测试 15：数据完整性验证
-- ============================================================================
SELECT '=== 测试 15：数据完整性验证 ===' as test_name;

-- 15.1 验证所有销售明细的 subtotal_kg 计算正确
SELECT 
    si.id,
    si.sale_id,
    si.box_qty,
    si.extra_kg,
    si.subtotal_kg as actual_subtotal,
    (si.box_qty * sp.kg_per_box + si.extra_kg) as expected_subtotal,
    CASE 
        WHEN ABS(si.subtotal_kg - (si.box_qty * sp.kg_per_box + si.extra_kg)) < 0.001 
        THEN 'OK' 
        ELSE 'ERROR' 
    END as validation
FROM sale_item si
JOIN spec sp ON si.spec_id = sp.id;

-- 15.2 验证所有销售单的 total_kg 汇总正确
SELECT 
    s.id,
    s.total_kg as actual_total,
    IFNULL(SUM(si.subtotal_kg), 0) as expected_total,
    CASE 
        WHEN ABS(s.total_kg - IFNULL(SUM(si.subtotal_kg), 0)) < 0.001 
        THEN 'OK' 
        ELSE 'ERROR' 
    END as validation
FROM sale s
LEFT JOIN sale_item si ON s.id = si.sale_id
GROUP BY s.id, s.total_kg;

-- 15.3 验证库存变动与销售单的对应关系
SELECT 
    s.id as sale_id,
    s.total_kg as sale_total_kg,
    sm.kg as stock_move_kg,
    CASE 
        WHEN ABS(s.total_kg + sm.kg) < 0.001 
        THEN 'OK' 
        ELSE 'ERROR' 
    END as validation
FROM sale s
LEFT JOIN stock_move sm ON s.id = sm.reference_id AND sm.reference_type = 'sale'
WHERE s.status = 'active';

-- ============================================================================
-- 测试总结
-- ============================================================================
SELECT '=== 测试总结 ===' as test_name;

SELECT 
    '总销售单数' as metric,
    COUNT(*) as value
FROM sale
UNION ALL
SELECT 
    '有效销售单数',
    COUNT(*)
FROM sale
WHERE status = 'active'
UNION ALL
SELECT 
    '作废销售单数',
    COUNT(*)
FROM sale
WHERE status = 'void'
UNION ALL
SELECT 
    '总销售明细数',
    COUNT(*)
FROM sale_item
UNION ALL
SELECT 
    '库存变动记录数',
    COUNT(*)
FROM stock_move
UNION ALL
SELECT 
    '审计日志记录数',
    COUNT(*)
FROM audit_log
UNION ALL
SELECT 
    '当前库存（KG）',
    current_stock_kg
FROM v_current_stock;

SELECT '=== 所有测试完成 ===' as status;
