#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
本地数据库迁移脚本：为memo表添加reference字段
"""
import sqlite3
import os

def migrate_local_db():
    print("=" * 60)
    print("   本地数据库迁移: 添加memo表reference字段")
    print("=" * 60)
    
    # 迁移两个数据库文件
    db_paths = [
        'sales.db',
        'instance/sales.db'
    ]
    
    for db_path in db_paths:
        if not os.path.exists(db_path):
            print(f"[SKIP] {db_path} 不存在")
            continue
            
        print(f"\n[INFO] 迁移 {db_path}...")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查memo表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memo'")
            if not cursor.fetchone():
                print(f"[SKIP] {db_path} 中不存在memo表")
                conn.close()
                continue
            
            # 检查reference_type列是否已存在
            cursor.execute("PRAGMA table_info(memo)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'reference_type' in columns:
                print(f"[SKIP] {db_path} 已包含reference字段")
                conn.close()
                continue
            
            # 添加新列
            print(f"[INFO] 添加reference_type和reference_id列...")
            cursor.execute("ALTER TABLE memo ADD COLUMN reference_type VARCHAR(20) NULL")
            cursor.execute("ALTER TABLE memo ADD COLUMN reference_id VARCHAR(50) NULL")
            
            conn.commit()
            print(f"[SUCCESS] {db_path} 迁移完成")
            
        except Exception as e:
            print(f"[ERROR] 迁移 {db_path} 失败: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()
    
    print("\n" + "=" * 60)
    print("[DONE] 迁移完成")
    print("=" * 60)

if __name__ == '__main__':
    migrate_local_db()
