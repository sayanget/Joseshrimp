#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库快速初始化和测试脚本
用途：一键创建数据库、运行测试、查看结果
"""

import sqlite3
import os
import sys
from datetime import datetime

# 设置Windows控制台UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def create_database(db_path='sales.db'):
    """创建数据库并初始化"""
    print("=" * 60)
    print("步骤 1: 创建数据库")
    print("=" * 60)
    
    # 如果数据库已存在，先备份
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(db_path, backup_path)
        print(f"✓ 已备份现有数据库到: {backup_path}")
    
    # 创建新数据库
    conn = sqlite3.connect(db_path)
    print(f"✓ 创建数据库: {db_path}")
    
    # 读取并执行 schema.sql
    with open('schema.sql', 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn.executescript(schema_sql)
    conn.commit()
    print("✓ 数据库表结构创建完成")
    
    # 验证表创建
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"✓ 共创建 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()
    print()

def run_tests(db_path='sales.db'):
    """运行测试脚本"""
    print("=" * 60)
    print("步骤 2: 运行测试")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    
    # 读取并执行测试脚本
    with open('test_database.sql', 'r', encoding='utf-8') as f:
        test_sql = f.read()
    
    # 执行测试（分段执行以便查看结果）
    cursor = conn.cursor()
    
    # 执行所有测试
    try:
        conn.executescript(test_sql)
        conn.commit()
        print("✓ 所有测试执行完成")
    except Exception as e:
        print(f"✗ 测试执行出错: {e}")
        conn.rollback()
    
    conn.close()
    print()

def show_summary(db_path='sales.db'):
    """显示数据库摘要"""
    print("=" * 60)
    print("步骤 3: 数据库摘要")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 显示各表记录数
    tables = ['spec', 'customer', 'sale', 'sale_item', 'stock_move', 'audit_log', 'inventory_check']
    
    print("\n表记录统计:")
    print("-" * 60)
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:20s}: {count:5d} 条记录")
    
    # 显示当前库存
    print("\n当前库存:")
    print("-" * 60)
    cursor.execute("SELECT * FROM v_current_stock")
    stock = cursor.fetchone()
    if stock:
        print(f"  当前库存: {stock[0]:.2f} KG")
        print(f"  变动次数: {stock[1]}")
        print(f"  最后变动: {stock[2]}")
    
    # 显示今日销售
    print("\n今日销售:")
    print("-" * 60)
    cursor.execute("SELECT * FROM v_today_sales")
    today_sales = cursor.fetchone()
    if today_sales:
        print(f"  销售日期: {today_sales[0]}")
        print(f"  订单数量: {today_sales[1]}")
        print(f"  总重量: {today_sales[2]:.2f} KG")
        print(f"  现金: {today_sales[3]:.2f} KG")
        print(f"  信用: {today_sales[4]:.2f} KG")
    else:
        print("  今日暂无销售")
    
    # 显示客户排名
    print("\n客户销售排名 (Top 5):")
    print("-" * 60)
    cursor.execute("""
        SELECT customer_name, order_count, total_kg
        FROM v_customer_ranking
        WHERE order_count > 0
        ORDER BY total_kg DESC
        LIMIT 5
    """)
    customers = cursor.fetchall()
    if customers:
        for i, (name, orders, kg) in enumerate(customers, 1):
            print(f"  {i}. {name:20s} - {orders} 单 - {kg:.2f} KG")
    else:
        print("  暂无销售数据")
    
    # 显示规格使用统计
    print("\n规格使用统计 (Top 5):")
    print("-" * 60)
    cursor.execute("""
        SELECT spec_name, usage_count, total_kg 
        FROM v_spec_usage 
        WHERE usage_count > 0
        ORDER BY total_kg DESC 
        LIMIT 5
    """)
    specs = cursor.fetchall()
    if specs:
        for i, (name, count, kg) in enumerate(specs, 1):
            print(f"  {i}. {name:20s} - {count} 次 - {kg:.2f} KG")
    else:
        print("  暂无使用数据")
    
    conn.close()
    print()

def verify_integrity(db_path='sales.db'):
    """验证数据完整性"""
    print("=" * 60)
    print("步骤 4: 数据完整性验证")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    errors = []
    
    # 验证 1: 销售明细的 subtotal_kg 计算正确性
    cursor.execute("""
        SELECT si.id, si.subtotal_kg, (si.box_qty * sp.kg_per_box + si.extra_kg) as expected
        FROM sale_item si
        JOIN spec sp ON si.spec_id = sp.id
        WHERE ABS(si.subtotal_kg - (si.box_qty * sp.kg_per_box + si.extra_kg)) > 0.001
    """)
    invalid_items = cursor.fetchall()
    if invalid_items:
        errors.append(f"发现 {len(invalid_items)} 条销售明细的 subtotal_kg 计算错误")
    else:
        print("✓ 销售明细 subtotal_kg 计算正确")
    
    # 验证 2: 销售单的 total_kg 汇总正确性
    cursor.execute("""
        SELECT s.id, s.total_kg, IFNULL(SUM(si.subtotal_kg), 0) as expected
        FROM sale s
        LEFT JOIN sale_item si ON s.id = si.sale_id
        GROUP BY s.id, s.total_kg
        HAVING ABS(s.total_kg - IFNULL(SUM(si.subtotal_kg), 0)) > 0.001
    """)
    invalid_sales = cursor.fetchall()
    if invalid_sales:
        errors.append(f"发现 {len(invalid_sales)} 条销售单的 total_kg 汇总错误")
    else:
        print("✓ 销售单 total_kg 汇总正确")
    
    # 验证 3: 库存变动与销售单的对应关系
    cursor.execute("""
        SELECT s.id
        FROM sale s
        LEFT JOIN stock_move sm ON s.id = sm.reference_id AND sm.reference_type = 'sale'
        WHERE s.status = 'active' AND sm.id IS NULL
    """)
    missing_stock_moves = cursor.fetchall()
    if missing_stock_moves:
        errors.append(f"发现 {len(missing_stock_moves)} 条销售单缺少库存变动记录")
    else:
        print("✓ 库存变动记录完整")
    
    # 验证 4: 外键完整性
    cursor.execute("""
        SELECT COUNT(*) FROM sale s
        LEFT JOIN customer c ON s.customer_id = c.id
        WHERE c.id IS NULL
    """)
    orphan_sales = cursor.fetchone()[0]
    if orphan_sales > 0:
        errors.append(f"发现 {orphan_sales} 条销售单的客户不存在")
    else:
        print("✓ 外键关系完整")
    
    # 显示错误
    if errors:
        print("\n✗ 发现以下问题:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✓ 所有数据完整性检查通过")
    
    conn.close()
    print()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("销售管理系统 - 数据库初始化和测试")
    print("=" * 60)
    print()
    
    try:
        # 步骤 1: 创建数据库
        create_database()
        
        # 步骤 2: 运行测试
        run_tests()
        
        # 步骤 3: 显示摘要
        show_summary()
        
        # 步骤 4: 验证完整性
        verify_integrity()
        
        print("=" * 60)
        print("✓ 数据库初始化和测试完成！")
        print("=" * 60)
        print()
        print("下一步:")
        print("  1. 查看 database_design.md 了解详细设计")
        print("  2. 查看 README.md 了解使用方法")
        print("  3. 使用 sqlite3 sales.db 进入数据库")
        print("  4. 开始开发 Web 应用")
        print()
        
    except FileNotFoundError as e:
        print(f"\n✗ 错误: 找不到文件 {e.filename}")
        print("请确保 schema.sql 和 test_database.sql 文件存在")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
