# 生产环境部署指南 - 回款功能

## 数据库结构变化

### 新增表: `remittance`

回款记录表,用于记录信用销售的回款信息。

**表结构:**
```sql
CREATE TABLE remittance (
    id SERIAL PRIMARY KEY,
    remittance_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sale_id VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50) NOT NULL,
    CONSTRAINT fk_remittance_sale FOREIGN KEY (sale_id) REFERENCES sale(id),
    CONSTRAINT check_remittance_amount_positive CHECK (amount > 0)
);

-- 索引
CREATE INDEX idx_remittance_sale_id ON remittance(sale_id);
CREATE INDEX idx_remittance_time ON remittance(remittance_time);
```

### 修改的表: `sale`

在应用层面添加了与`remittance`表的关系,但**不需要修改表结构**。

---

## 部署步骤

### 1. 代码部署 (已完成 ✓)

- [x] 代码已推送到GitHub (commit: e5db24c)
- [x] Render自动检测到更新并开始部署

### 2. 数据库迁移 (待执行)

#### 方法A: 使用Render Shell (推荐)

1. 等待Render部署完成 (3-5分钟)
2. 在Render Dashboard中打开Shell
3. 运行迁移脚本:
   ```bash
   python create_remittance_table_production.py
   ```
4. 验证输出显示表创建成功

#### 方法B: 使用本地脚本连接生产数据库

1. 设置环境变量:
   ```bash
   set DATABASE_URL=postgresql://user:password@host:port/database
   ```
2. 运行迁移脚本:
   ```bash
   python create_remittance_table_production.py
   ```

### 3. 验证部署

访问生产环境并测试:

1. **访问回款页面**
   - URL: `https://your-app.onrender.com/sales/remittance`
   - 验证页面正常加载

2. **测试语言切换**
   - 切换到中文、英文、西班牙语
   - 验证所有文本正确翻译

3. **测试回款功能**
   - 找到一条信用销售记录
   - 点击"回款"按钮
   - 输入回款金额并提交
   - 验证:
     - 回款成功提示
     - 页面数据更新
     - 销售单状态变化

4. **检查数据库**
   - 在Render Shell中运行:
     ```bash
     python -c "from app import create_app, db; app = create_app(); app.app_context().push(); from app.models import Remittance; print('Remittance count:', Remittance.query.count())"
     ```

---

## 回滚计划

如果部署出现问题:

### 代码回滚
```bash
git revert e5db24c
git push origin master
```

### 数据库回滚
```sql
-- 删除remittance表 (谨慎操作!)
DROP TABLE IF EXISTS remittance CASCADE;
```

**注意**: 删除表会丢失所有回款记录数据!

---

## 监控要点

部署后需要监控:

1. **应用日志**: 检查是否有错误
2. **数据库连接**: 确保remittance表可访问
3. **API响应**: 测试回款API端点
4. **用户反馈**: 收集用户使用反馈

---

## 常见问题

### Q: 表已存在错误
**A**: 脚本使用`CREATE TABLE IF NOT EXISTS`,不会报错。如果仍有问题,检查表名是否正确。

### Q: 外键约束失败
**A**: 确保`sale`表存在且有数据。检查`sale_id`字段类型是否匹配。

### Q: 权限错误
**A**: 确保数据库用户有CREATE TABLE权限。

---

## 联系支持

如有问题,请检查:
- Render部署日志
- 应用错误日志
- 数据库连接状态
