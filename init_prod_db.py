"""
Supabase Database Initialization Script
由于Supabase是远程PostgreSQL，无法使用本地SQLite的init_db.py逻辑。
此脚本用于连接远程Supabase数据库并创建所有表。

Usage:
1. 获取 Supabase 的 Connection String (Transaction mode, port 6543 or Session mode, port 5432)
2. 设置环境变量 DATABASE_URL
   Windows: set DATABASE_URL=postgresql://user:pass@host:port/db
   Linux/Mac: export DATABASE_URL=postgresql://user:pass@host:port/db
3. 运行此脚本: python init_prod_db.py
"""
import os
import sys
from app import create_app, db

# 确保能找到app模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_supabase_db():
    print("=" * 50)
    print("   Supabase DataBase Initialization Tool")
    print("=" * 50)

    # 检查环境变量
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] 环境变量 DATABASE_URL 未设置！")
        print("请先设置 DATABASE_URL，例如：")
        print("set DATABASE_URL=postgresql://postgres.xxx:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
        return

    # 适配 Render/Supabase 的 URL 格式
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        os.environ['DATABASE_URL'] = db_url

    print(f"[INFO] 目标数据库: {db_url.split('@')[1] if '@' in db_url else 'Unknown'}")
    
    confirm = input("确认要初始化生产环境数据库吗？这将创建新表 (y/n): ")
    if confirm.lower() != 'y':
        print("[INFO] 操作已取消")
        return

    try:
        # 使用生产配置创建应用
        app = create_app('production')
        
        with app.app_context():
            print("[INFO] 正在连接数据库...")
            # 创建所有表
            db.create_all()
            print("[SUCCESS] 数据库表创建成功！")
            
            # 可以在这里添加初始数据
            from app.models import Spec
            if Spec.query.count() == 0:
                print("[INFO] 正在初始化默认规格数据...")
                default_specs = [
                    {'name': '39X110', 'length': 110, 'width': 39, 'kg_per_box': 40},
                    {'name': '38X115', 'length': 115, 'width': 38, 'kg_per_box': 40}
                ]
                for s in default_specs:
                    db.session.add(Spec(name=s['name'], length=s['length'], width=s['width'], kg_per_box=s['kg_per_box'], created_by='system'))
                db.session.commit()
                print("[SUCCESS] 默认数据添加完成")
            else:
                print("[INFO] 数据库已有数据，跳过默认数据初始化")

    except Exception as e:
        print(f"\n[ERROR] 初始化失败: {str(e)}")
        print("请检查：")
        print("1. 数据库连接字符串是否正确")
        print("2. 数据库防火墙是否允许当前IP连接")
        print("3. 密码是否包含特殊字符（需要URL编码）")

if __name__ == '__main__':
    init_supabase_db()
