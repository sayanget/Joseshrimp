#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生产环境数据库初始化脚本 (Supabase + Render 优化版)

用途：
1. 初始化Supabase PostgreSQL数据库
2. 创建所有必需的表
3. 添加默认数据（规格、用户、角色等）

使用方法：
    export DATABASE_URL="postgresql://..."
    python init_supabase_safe.py
"""

import os
import sys
from app import create_app, db
from app.models import Spec, User, Role, Permission
from sqlalchemy import text, inspect

def check_database_connection():
    """检查数据库连接"""
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL 环境变量未设置")
        print("请设置: export DATABASE_URL='postgresql://...'")
        return False
    
    # Supabase/Render URL 格式适配
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        os.environ['DATABASE_URL'] = db_url
    
    print(f"[INFO] 数据库: {db_url.split('@')[1] if '@' in db_url else 'Unknown'}")
    return True

def verify_schema():
    """验证数据库schema是否正确"""
    inspector = inspect(db.engine)
    
    # 检查user表的password_hash字段长度
    columns = inspector.get_columns('user')
    for col in columns:
        if col['name'] == 'password_hash':
            # PostgreSQL返回的类型信息
            col_type = str(col['type'])
            if 'VARCHAR(255)' in col_type or 'CHARACTER VARYING(255)' in col_type:
                print("[✓] password_hash 字段长度正确 (255)")
            else:
                print(f"[WARNING] password_hash 字段类型: {col_type}")
                print("[WARNING] 建议长度为 VARCHAR(255)")
    
    # 检查必需字段
    required_columns = ['id', 'username', 'password_hash', 'active', 'role_id', 'created_at', 'last_login']
    existing_columns = [col['name'] for col in columns]
    
    for req_col in required_columns:
        if req_col in existing_columns:
            print(f"[✓] {req_col} 字段存在")
        else:
            print(f"[ERROR] {req_col} 字段缺失")
            return False
    
    return True

def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("   Supabase 数据库初始化 (生产环境)")
    print("=" * 60)
    
    if not check_database_connection():
        return False
    
    try:
        app = create_app('production')
        
        with app.app_context():
            print("\n[1] 创建数据库表...")
            db.create_all()
            print("[✓] 表创建完成")
            
            print("\n[2] 验证Schema...")
            if not verify_schema():
                print("[ERROR] Schema验证失败")
                return False
            
            print("\n[3] 检查默认数据...")
            
            # 检查并创建默认规格
            spec_count = Spec.query.count()
            if spec_count == 0:
                print("[INFO] 创建默认规格...")
                default_specs = [
                    {"name": "39X110", "length": 110, "width": 39, "kg_per_box": 40.0},
                    {"name": "GENERAL", "length": 0, "width": 0, "kg_per_box": 1.0}
                ]
                
                for spec_data in default_specs:
                    spec = Spec(
                        name=spec_data["name"],
                        length=spec_data["length"],
                        width=spec_data["width"],
                        kg_per_box=spec_data["kg_per_box"],
                        created_by='system'
                    )
                    db.session.add(spec)
                
                db.session.commit()
                print(f"[✓] 创建了 {len(default_specs)} 个默认规格")
            else:
                print(f"[✓] 已存在 {spec_count} 个规格")
            
            # 检查权限和角色
            perm_count = Permission.query.count()
            role_count = Role.query.count()
            user_count = User.query.count()
            
            print(f"[INFO] 当前数据统计:")
            print(f"  - 权限: {perm_count}")
            print(f"  - 角色: {role_count}")
            print(f"  - 用户: {user_count}")
            
            if user_count == 0:
                print("\n[WARNING] 未检测到用户数据")
                print("[INFO] 请运行 direct_psycopg2_sync.py 同步本地用户数据")
            
            print("\n" + "=" * 60)
            print("[SUCCESS] 数据库初始化完成！")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\n[ERROR] 初始化失败: {str(e)}")
        print("\n请检查：")
        print("1. DATABASE_URL 是否正确")
        print("2. 网络连接是否正常")
        print("3. Supabase 防火墙设置")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
