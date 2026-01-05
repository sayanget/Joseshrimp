# 部署方案文档

**版本**: 1.0  
**创建日期**: 2026-01-05  
**作者**: Claude

---

## 一、部署架构概览

### 1.1 部署架构图

```mermaid
graph TB
    subgraph 用户层
        A[Web浏览器]
        B[移动浏览器]
    end
    
    subgraph 负载均衡层
        C[Nginx]
    end
    
    subgraph 应用层
        D[Flask App 1]
        E[Flask App 2]
        F[Flask App 3]
    end
    
    subgraph 数据层
        G[MySQL主库]
        H[MySQL从库]
    end
    
    subgraph 存储层
        I[文件存储]
        J[备份存储]
    end
    
    A --> C
    B --> C
    C --> D
    C --> E
    C --> F
    D --> G
    E --> G
    F --> G
    G --> H
    D --> I
    G --> J
```

### 1.2 技术栈

| 组件 | 技术选型 | 版本 |
|-----|---------|------|
| 操作系统 | Ubuntu Server | 22.04 LTS |
| Web服务器 | Nginx | 1.24+ |
| 应用服务器 | Gunicorn | 21.0+ |
| 应用框架 | Flask | 3.0+ |
| 数据库 | MySQL | 8.0+ |
| Python | Python | 3.10+ |
| 容器化 | Docker | 24.0+ |
| 编排工具 | Docker Compose | 2.20+ |

---

## 二、环境准备

### 2.1 服务器要求

#### 开发环境
- CPU: 2核
- 内存: 4GB
- 硬盘: 50GB
- 操作系统: Windows/Linux/macOS

#### 生产环境（小型部署）
- CPU: 4核
- 内存: 8GB
- 硬盘: 100GB SSD
- 操作系统: Ubuntu Server 22.04 LTS
- 网络: 固定IP，开放80/443端口

#### 生产环境（中型部署）
- CPU: 8核
- 内存: 16GB
- 硬盘: 200GB SSD
- 操作系统: Ubuntu Server 22.04 LTS
- 网络: 固定IP，开放80/443端口

### 2.2 软件依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

---

## 三、部署方式

### 3.1 方式一：Docker Compose 部署（推荐）

#### 步骤1：克隆代码

```bash
git clone https://github.com/your-repo/sales-management-system.git
cd sales-management-system
```

#### 步骤2：配置环境变量

```bash
cp .env.example .env
vim .env
```

`.env` 文件内容：
```bash
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-in-production

# 数据库配置
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_DATABASE=sales_db
MYSQL_USER=sales_user
MYSQL_PASSWORD=your-password

# 应用配置
DATABASE_URL=mysql+pymysql://sales_user:your-password@db/sales_db
DEFAULT_OPERATOR=Jose Burgueno

# 备份配置
BACKUP_ENABLED=true
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
```

#### 步骤3：构建和启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

#### 步骤4：初始化数据库

```bash
# 进入应用容器
docker-compose exec web bash

# 初始化数据库
python scripts/init_db.py

# 创建管理员用户
python scripts/create_admin.py

# 退出容器
exit
```

#### 步骤5：验证部署

```bash
# 访问应用
curl http://localhost

# 检查健康状态
curl http://localhost/health
```

### 3.2 方式二：传统部署

#### 步骤1：安装Python环境

```bash
# 安装Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate
```

#### 步骤2：安装依赖

```bash
pip install -r requirements.txt
```

#### 步骤3：安装MySQL

```bash
# 安装MySQL
sudo apt install -y mysql-server

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
sudo mysql -u root -p
```

```sql
CREATE DATABASE sales_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sales_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON sales_db.* TO 'sales_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 步骤4：配置应用

```bash
# 设置环境变量
export FLASK_ENV=production
export DATABASE_URL=mysql+pymysql://sales_user:your-password@localhost/sales_db
export SECRET_KEY=your-secret-key

# 初始化数据库
python scripts/init_db.py
```

#### 步骤5：配置Gunicorn

创建 `gunicorn_config.py`：
```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

#### 步骤6：配置Systemd服务

创建 `/etc/systemd/system/sales-app.service`：
```ini
[Unit]
Description=Sales Management System
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/sales-management-system
Environment="PATH=/opt/sales-management-system/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/opt/sales-management-system/venv/bin/gunicorn -c gunicorn_config.py run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable sales-app
sudo systemctl start sales-app
sudo systemctl status sales-app
```

#### 步骤7：配置Nginx

创建 `/etc/nginx/sites-available/sales-app`：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 16M;
    
    location /static/ {
        alias /opt/sales-management-system/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/sales-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 四、SSL/HTTPS 配置

### 4.1 使用 Let's Encrypt

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 4.2 Nginx HTTPS配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 其他配置同上...
}
```

---

## 五、数据库管理

### 5.1 数据库备份

#### 自动备份脚本

创建 `scripts/backup_db.sh`：
```bash
#!/bin/bash

# 配置
BACKUP_DIR="/var/backups/sales_db"
DB_NAME="sales_db"
DB_USER="sales_user"
DB_PASS="your-password"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份文件名
BACKUP_FILE="$BACKUP_DIR/sales_db_$(date +%Y%m%d_%H%M%S).sql.gz"

# 执行备份
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_FILE

# 删除旧备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "备份完成: $BACKUP_FILE"
```

#### 配置定时任务

```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点备份
0 2 * * * /opt/sales-management-system/scripts/backup_db.sh >> /var/log/backup.log 2>&1
```

### 5.2 数据库恢复

```bash
# 解压备份文件
gunzip sales_db_20260105_020000.sql.gz

# 恢复数据库
mysql -u sales_user -p sales_db < sales_db_20260105_020000.sql
```

### 5.3 数据库优化

```sql
-- 分析表
ANALYZE TABLE sale, sale_item, stock_move;

-- 优化表
OPTIMIZE TABLE sale, sale_item, stock_move;

-- 检查索引使用情况
SHOW INDEX FROM sale;
```

---

## 六、监控与日志

### 6.1 应用日志

#### 日志配置

```python
# app/config.py
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler(
    'logs/sales_app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
```

#### 查看日志

```bash
# 实时查看应用日志
tail -f logs/sales_app.log

# 查看Nginx访问日志
tail -f /var/log/nginx/access.log

# 查看Nginx错误日志
tail -f /var/log/nginx/error.log

# 查看系统日志
journalctl -u sales-app -f
```

### 6.2 性能监控

#### 安装监控工具

```bash
# 安装htop
sudo apt install -y htop

# 安装iotop
sudo apt install -y iotop

# 安装nethogs
sudo apt install -y nethogs
```

#### 数据库监控

```sql
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';

-- 查看表大小
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'sales_db'
ORDER BY size_mb DESC;
```

### 6.3 健康检查

创建健康检查端点 `app/views/health.py`：
```python
from flask import Blueprint, jsonify
from app import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """健康检查"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

---

## 七、安全加固

### 7.1 防火墙配置

```bash
# 安装UFW
sudo apt install -y ufw

# 配置规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
sudo ufw status
```

### 7.2 数据库安全

```sql
-- 限制远程访问
-- 编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
-- bind-address = 127.0.0.1

-- 删除匿名用户
DELETE FROM mysql.user WHERE User='';

-- 删除测试数据库
DROP DATABASE IF EXISTS test;

-- 刷新权限
FLUSH PRIVILEGES;
```

### 7.3 应用安全

```python
# 配置安全头
from flask_talisman import Talisman

talisman = Talisman(
    app,
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"]
    }
)
```

---

## 八、扩展方案

### 8.1 水平扩展

#### 负载均衡配置

```nginx
upstream flask_app {
    least_conn;
    server app1:5000 weight=1;
    server app2:5000 weight=1;
    server app3:5000 weight=1;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://flask_app;
        # 其他配置...
    }
}
```

#### Docker Compose扩展

```bash
# 扩展到3个实例
docker-compose up -d --scale web=3
```

### 8.2 数据库主从复制

#### 主库配置

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：
```ini
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_do_db = sales_db
```

创建复制用户：
```sql
CREATE USER 'repl'@'%' IDENTIFIED BY 'repl-password';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';
FLUSH PRIVILEGES;
SHOW MASTER STATUS;
```

#### 从库配置

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：
```ini
[mysqld]
server-id = 2
relay-log = /var/log/mysql/mysql-relay-bin.log
```

配置复制：
```sql
CHANGE MASTER TO
    MASTER_HOST='master-ip',
    MASTER_USER='repl',
    MASTER_PASSWORD='repl-password',
    MASTER_LOG_FILE='mysql-bin.000001',
    MASTER_LOG_POS=154;

START SLAVE;
SHOW SLAVE STATUS\G
```

---

## 九、故障排查

### 9.1 常见问题

#### 问题1：应用无法启动

```bash
# 检查日志
docker-compose logs web

# 检查端口占用
sudo netstat -tulpn | grep 5000

# 检查配置文件
python -c "from app import create_app; app = create_app(); print('OK')"
```

#### 问题2：数据库连接失败

```bash
# 检查MySQL状态
sudo systemctl status mysql

# 测试连接
mysql -u sales_user -p -h localhost sales_db

# 检查防火墙
sudo ufw status
```

#### 问题3：性能问题

```bash
# 检查CPU和内存
htop

# 检查磁盘IO
iotop

# 检查慢查询
sudo tail -f /var/log/mysql/slow-query.log

# 分析Nginx日志
sudo tail -f /var/log/nginx/access.log | grep "POST /api"
```

### 9.2 紧急恢复

#### 回滚部署

```bash
# Docker方式
docker-compose down
git checkout previous-version
docker-compose up -d

# 传统方式
sudo systemctl stop sales-app
git checkout previous-version
sudo systemctl start sales-app
```

#### 数据库回滚

```bash
# 停止应用
sudo systemctl stop sales-app

# 恢复备份
mysql -u sales_user -p sales_db < /var/backups/sales_db/sales_db_20260104_020000.sql

# 启动应用
sudo systemctl start sales-app
```

---

## 十、维护计划

### 10.1 日常维护

| 任务 | 频率 | 负责人 |
|-----|------|--------|
| 检查应用日志 | 每天 | 运维 |
| 检查磁盘空间 | 每天 | 运维 |
| 检查备份状态 | 每天 | 运维 |
| 数据库优化 | 每周 | DBA |
| 安全更新 | 每周 | 运维 |
| 性能分析 | 每月 | 开发+运维 |

### 10.2 定期任务

```bash
# 每日备份（凌晨2点）
0 2 * * * /opt/sales-management-system/scripts/backup_db.sh

# 每周日志归档（周日凌晨3点）
0 3 * * 0 /opt/sales-management-system/scripts/archive_logs.sh

# 每月数据库优化（每月1号凌晨4点）
0 4 1 * * /opt/sales-management-system/scripts/optimize_db.sh
```

---

## 十一、部署检查清单

### 11.1 部署前检查

- [ ] 服务器资源充足（CPU、内存、磁盘）
- [ ] 域名DNS已配置
- [ ] SSL证书已准备
- [ ] 数据库已创建
- [ ] 环境变量已配置
- [ ] 防火墙规则已设置
- [ ] 备份策略已制定

### 11.2 部署后验证

- [ ] 应用可正常访问
- [ ] HTTPS正常工作
- [ ] 数据库连接正常
- [ ] 日志正常输出
- [ ] 备份任务正常运行
- [ ] 监控告警正常
- [ ] 性能测试通过

### 11.3 上线检查

- [ ] 功能测试通过
- [ ] 性能测试通过
- [ ] 安全扫描通过
- [ ] 备份恢复测试通过
- [ ] 文档已更新
- [ ] 团队已培训
- [ ] 应急预案已准备

---

## 十二、联系方式

### 技术支持

- **开发团队**: dev@example.com
- **运维团队**: ops@example.com
- **紧急联系**: +1-xxx-xxx-xxxx

### 相关文档

- [数据库设计文档](../database_design.md)
- [API接口规范](api_specification.md)
- [Web应用架构](web_application_architecture.md)
- [Excel导入方案](excel_import_design.md)

---

**文档版本**: 1.0  
**最后更新**: 2026-01-05  
**文档结束**
