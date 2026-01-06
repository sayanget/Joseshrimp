# Supabase + Render 部署指南

## 环境架构

- **数据库**: Supabase PostgreSQL
- **应用托管**: Render
- **本地开发**: SQLite (仅用于开发)

## 关键兼容性配置

### 1. 数据库连接 (config.py)

```python
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Supabase/Render URL 格式适配
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
```

### 2. 模型定义优化 (models.py)

```python
class User(UserMixin, db.Model):
    password_hash = db.Column(db.String(255))  # ✓ 255字符（不是128）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)  # ✓ 可为NULL
```

### 3. 日志配置 (config.py)

```python
# 生产环境使用 stdout（不写文件）
file_handler = logging.StreamHandler(sys.stdout)
```

### 4. 服务器配置 (serve.py)

```python
# 使用 Waitress（不是 Gunicorn）
from waitress import serve
serve(app, host="0.0.0.0", port=port)
```

## 部署流程

### 首次部署

1. **初始化Supabase数据库**
   ```bash
   export DATABASE_URL="postgresql://..."
   python init_supabase_safe.py
   ```

2. **同步用户数据**
   ```bash
   python direct_psycopg2_sync.py
   ```

3. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "Production ready"
   git push
   ```

4. **配置Render**
   - 在Render Dashboard设置 `DATABASE_URL` 环境变量
   - Start Command: `python serve.py`
   - Build Command: `pip install -r requirements.txt`

### 日常更新

1. **本地开发**
   ```bash
   # 使用SQLite开发
   python run.py
   ```

2. **测试**
   ```bash
   # 本地测试
   pytest
   ```

3. **部署**
   ```bash
   git push  # Render自动部署
   ```

## 数据同步

### 从本地同步到生产

使用 `direct_psycopg2_sync.py`（推荐）:
- ✓ 直接PostgreSQL连接
- ✓ 明确的schema定义
- ✓ 避免ORM兼容性问题

```bash
python direct_psycopg2_sync.py
```

### 注意事项

1. **不要使用 `db.create_all()`** 在已有数据的生产环境
2. **时间戳处理**: 让PostgreSQL使用默认值
3. **布尔值**: SQLite的1/0需要转换为True/False
4. **字符串长度**: 确保足够（特别是password_hash）

## 故障排查

### 问题: 部署失败 "command not found"
**解决**: 检查Render的Start Command设置为 `python serve.py`

### 问题: 数据库连接失败
**解决**: 
1. 检查 `DATABASE_URL` 环境变量
2. 确保URL格式为 `postgresql://`（不是 `postgres://`）
3. 检查Supabase防火墙设置

### 问题: 用户登录失败
**解决**:
1. 运行 `init_supabase_safe.py` 验证schema
2. 检查password_hash字段长度（应为255）
3. 重新同步用户数据

## 最佳实践

### ✓ 推荐做法

1. 使用专用同步脚本（`direct_psycopg2_sync.py`）
2. 部署前验证schema（`init_supabase_safe.py`）
3. 环境变量统一管理
4. 日志输出到stdout
5. 使用Waitress作为WSGI服务器

### ✗ 避免做法

1. 不要在生产环境直接使用 `db.create_all()`
2. 不要在容器中写日志文件
3. 不要硬编码数据库连接
4. 不要使用开发服务器（`flask run`）
5. 不要忽略schema验证

## 监控与维护

### 定期检查

```bash
# 验证数据库schema
python init_supabase_safe.py

# 检查数据完整性
python check_prod_count.py
```

### 备份策略

- Supabase自动备份（每日）
- 重要更新前手动备份
- 保留同步脚本以便恢复

## 文件清单

### 生产环境必需文件

- `serve.py` - Waitress服务器入口
- `render.yaml` - Render配置
- `requirements.txt` - Python依赖
- `app/config.py` - 环境配置
- `app/models.py` - 数据模型（password_hash=255）

### 运维工具

- `init_supabase_safe.py` - 安全初始化脚本
- `direct_psycopg2_sync.py` - 数据同步工具
- `check_prod_count.py` - 数据验证工具
