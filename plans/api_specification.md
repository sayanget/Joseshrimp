# API 接口规范文档

**版本**: 1.0  
**创建日期**: 2026-01-05  
**基础URL**: `/api`  
**认证方式**: Session Cookie

---

## 一、通用规范

### 1.1 请求格式

- **Content-Type**: `application/json`
- **字符编码**: UTF-8
- **日期格式**: ISO 8601 (`YYYY-MM-DDTHH:mm:ss`)

### 1.2 响应格式

#### 成功响应
```json
{
  "data": { ... },
  "message": "操作成功",
  "timestamp": "2026-01-05T10:30:00"
}
```

#### 错误响应
```json
{
  "error": "错误信息",
  "code": "ERROR_CODE",
  "timestamp": "2026-01-05T10:30:00"
}
```

### 1.3 HTTP状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 二、销售管理 API

### 2.1 获取销售单列表

**接口**: `GET /api/sales`

**查询参数**:
```
page: 页码（默认1）
per_page: 每页数量（默认20）
status: 状态过滤（active/void）
customer_id: 客户ID过滤
date_from: 开始日期（YYYY-MM-DD）
date_to: 结束日期（YYYY-MM-DD）
```

**响应示例**:
```json
{
  "items": [
    {
      "id": "SALE-20260105-001",
      "sale_time": "2026-01-05T10:30:00",
      "customer": {
        "id": 1,
        "name": "DANIEL HIELO"
      },
      "payment_type": "Crédito",
      "total_kg": 150.5,
      "status": "active",
      "created_by": "Jose Burgueno"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

### 2.2 获取销售单详情

**接口**: `GET /api/sales/{sale_id}`

**路径参数**:
- `sale_id`: 销售单号

**响应示例**:
```json
{
  "id": "SALE-20260105-001",
  "sale_time": "2026-01-05T10:30:00",
  "customer": {
    "id": 1,
    "name": "DANIEL HIELO",
    "credit_allowed": true
  },
  "payment_type": "Crédito",
  "total_kg": 150.5,
  "status": "active",
  "created_by": "Jose Burgueno",
  "items": [
    {
      "id": 1,
      "spec": {
        "id": 1,
        "name": "JAVA 39x110",
        "kg_per_box": 20.0
      },
      "box_qty": 5,
      "extra_kg": 10.5,
      "subtotal_kg": 110.5
    },
    {
      "id": 2,
      "spec": {
        "id": 3,
        "name": "JAVA 38x110",
        "kg_per_box": 15.0
      },
      "box_qty": 2,
      "extra_kg": 10.0,
      "subtotal_kg": 40.0
    }
  ]
}
```

### 2.3 创建销售单

**接口**: `POST /api/sales`

**请求体**:
```json
{
  "customer_id": 1,
  "payment_type": "Crédito",
  "created_by": "Jose Burgueno",
  "items": [
    {
      "spec_id": 1,
      "box_qty": 5,
      "extra_kg": 10.5
    },
    {
      "spec_id": 3,
      "box_qty": 2,
      "extra_kg": 10.0
    }
  ]
}
```

**响应**: 201 Created
```json
{
  "id": "SALE-20260105-002",
  "sale_time": "2026-01-05T11:00:00",
  "customer": { ... },
  "payment_type": "Crédito",
  "total_kg": 150.5,
  "status": "active",
  "items": [ ... ]
}
```

### 2.4 作废销售单

**接口**: `POST /api/sales/{sale_id}/void`

**请求体**:
```json
{
  "void_reason": "客户取消订单",
  "void_by": "admin"
}
```

**响应**: 200 OK
```json
{
  "id": "SALE-20260105-001",
  "status": "void",
  "void_reason": "客户取消订单",
  "void_time": "2026-01-05T12:00:00",
  "void_by": "admin"
}
```

### 2.5 今日销售汇总

**接口**: `GET /api/sales/today-summary`

**响应示例**:
```json
{
  "order_count": 15,
  "total_kg": 1250.5,
  "cash_kg": 800.0,
  "credit_kg": 450.5
}
```

---

## 三、库存管理 API

### 3.1 获取当前库存

**接口**: `GET /api/inventory/current`

**响应示例**:
```json
{
  "current_stock_kg": 5420.5,
  "last_move_time": "2026-01-05T10:30:00",
  "warning": false
}
```

### 3.2 获取库存变动列表

**接口**: `GET /api/inventory/moves`

**查询参数**:
```
page: 页码
per_page: 每页数量
move_type: 变动类型（进货/调拨/退货/盘盈/盘亏/销售）
date_from: 开始日期
date_to: 结束日期
```

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "move_type": "进货",
      "source": "Granja El Castillo",
      "kg": 1000.0,
      "move_time": "2026-01-05T08:00:00",
      "status": "active",
      "created_by": "admin"
    },
    {
      "id": 2,
      "move_type": "销售",
      "source": "DANIEL HIELO",
      "kg": -150.5,
      "move_time": "2026-01-05T10:30:00",
      "reference_id": "SALE-20260105-001",
      "reference_type": "sale",
      "status": "active"
    }
  ],
  "total": 50,
  "page": 1,
  "pages": 3
}
```

### 3.3 添加库存变动

**接口**: `POST /api/inventory/moves`

**请求体**:
```json
{
  "move_type": "进货",
  "source": "Granja El Castillo",
  "kg": 1000.0,
  "notes": "月初补货",
  "created_by": "admin"
}
```

**响应**: 201 Created
```json
{
  "id": 10,
  "move_type": "进货",
  "source": "Granja El Castillo",
  "kg": 1000.0,
  "move_time": "2026-01-05T14:00:00",
  "status": "active"
}
```

### 3.4 获取库存历史趋势

**接口**: `GET /api/inventory/history`

**查询参数**:
```
days: 天数（默认30）
```

**响应示例**:
```json
{
  "history": [
    {
      "date": "2026-01-01",
      "daily_change": 500.0,
      "cumulative_stock": 5000.0
    },
    {
      "date": "2026-01-02",
      "daily_change": -200.0,
      "cumulative_stock": 4800.0
    }
  ]
}
```

---

## 四、报表统计 API

### 4.1 按日期统计销售

**接口**: `GET /api/reports/daily-sales`

**查询参数**:
```
date_from: 开始日期（必填）
date_to: 结束日期（必填）
```

**响应示例**:
```json
{
  "data": [
    {
      "date": "2026-01-05",
      "order_count": 15,
      "total_kg": 1250.5,
      "cash_kg": 800.0,
      "credit_kg": 450.5
    },
    {
      "date": "2026-01-04",
      "order_count": 12,
      "total_kg": 980.0,
      "cash_kg": 600.0,
      "credit_kg": 380.0
    }
  ]
}
```

### 4.2 按客户统计

**接口**: `GET /api/reports/customer-sales`

**查询参数**:
```
date_from: 开始日期
date_to: 结束日期
limit: 返回数量（默认10）
```

**响应示例**:
```json
{
  "data": [
    {
      "customer_id": 1,
      "customer_name": "DANIEL HIELO",
      "order_count": 25,
      "total_kg": 2500.0,
      "avg_kg_per_order": 100.0,
      "last_sale_time": "2026-01-05T10:30:00"
    }
  ]
}
```

### 4.3 按规格统计

**接口**: `GET /api/reports/spec-sales`

**查询参数**:
```
date_from: 开始日期
date_to: 结束日期
limit: 返回数量（默认10）
```

**响应示例**:
```json
{
  "data": [
    {
      "spec_id": 1,
      "spec_name": "JAVA 39x110",
      "kg_per_box": 20.0,
      "usage_count": 50,
      "total_boxes": 200,
      "total_extra_kg": 150.0,
      "total_kg": 4150.0
    }
  ]
}
```

### 4.4 散货占比分析

**接口**: `GET /api/reports/extra-kg-analysis`

**查询参数**:
```
date_from: 开始日期
date_to: 结束日期
min_percent: 最小占比（默认0）
```

**响应示例**:
```json
{
  "data": [
    {
      "sale_id": "SALE-20260105-001",
      "sale_time": "2026-01-05T10:30:00",
      "customer_name": "DANIEL HIELO",
      "total_kg": 150.5,
      "extra_kg": 50.5,
      "extra_percent": 33.56
    }
  ]
}
```

---

## 五、系统管理 API

### 5.1 规格管理

#### 获取规格列表
**接口**: `GET /api/admin/specs`

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "JAVA 39x110",
      "length": 39,
      "width": 110,
      "kg_per_box": 20.0,
      "active": true
    }
  ]
}
```

#### 创建规格
**接口**: `POST /api/admin/specs`

**请求体**:
```json
{
  "name": "JAVA 40x120",
  "length": 40,
  "width": 120,
  "kg_per_box": 22.0,
  "created_by": "admin"
}
```

#### 更新规格
**接口**: `PUT /api/admin/specs/{spec_id}`

**请求体**:
```json
{
  "kg_per_box": 22.5,
  "updated_by": "admin"
}
```

#### 禁用规格
**接口**: `POST /api/admin/specs/{spec_id}/deactivate`

### 5.2 客户管理

#### 获取客户列表
**接口**: `GET /api/admin/customers`

#### 创建客户
**接口**: `POST /api/admin/customers`

**请求体**:
```json
{
  "name": "新客户",
  "credit_allowed": false,
  "created_by": "admin"
}
```

#### 更新客户
**接口**: `PUT /api/admin/customers/{customer_id}`

**请求体**:
```json
{
  "credit_allowed": true,
  "updated_by": "admin"
}
```

### 5.3 审计日志

**接口**: `GET /api/admin/audit-logs`

**查询参数**:
```
table_name: 表名
record_id: 记录ID
action: 操作类型（INSERT/UPDATE/DELETE/VOID）
date_from: 开始日期
date_to: 结束日期
page: 页码
per_page: 每页数量
```

**响应示例**:
```json
{
  "items": [
    {
      "id": 1,
      "table_name": "sale",
      "record_id": "SALE-20260105-001",
      "action": "INSERT",
      "new_value": "{\"id\":\"SALE-20260105-001\",\"customer_id\":1,...}",
      "created_at": "2026-01-05T10:30:00",
      "created_by": "Jose Burgueno"
    }
  ],
  "total": 500,
  "page": 1,
  "pages": 25
}
```

---

## 六、数据导入 API

### 6.1 上传Excel文件

**接口**: `POST /api/import/upload`

**请求**: multipart/form-data
```
file: Excel文件
dry_run: 是否仅验证（true/false）
```

**响应**: 202 Accepted
```json
{
  "task_id": "import-20260105-001",
  "status": "processing",
  "message": "文件上传成功，正在处理..."
}
```

### 6.2 查询导入状态

**接口**: `GET /api/import/status/{task_id}`

**响应示例**:
```json
{
  "task_id": "import-20260105-001",
  "status": "completed",
  "total_rows": 150,
  "success_count": 142,
  "error_count": 5,
  "warning_count": 3,
  "progress": 100,
  "started_at": "2026-01-05T14:00:00",
  "completed_at": "2026-01-05T14:02:30"
}
```

### 6.3 获取导入报告

**接口**: `GET /api/import/report/{task_id}`

**响应示例**:
```json
{
  "task_id": "import-20260105-001",
  "summary": {
    "total_rows": 150,
    "success_count": 142,
    "error_count": 5,
    "warning_count": 3
  },
  "errors": [
    {
      "row_number": 15,
      "error_type": "ERROR",
      "error_message": "缺少客户名称",
      "original_data": "{...}"
    }
  ],
  "warnings": [
    {
      "row_number": 28,
      "error_type": "WARNING",
      "error_message": "规格不存在，已自动创建",
      "original_data": "{...}"
    }
  ],
  "new_specs_created": [
    {
      "name": "JAVA 40x125",
      "length": 40,
      "width": 125,
      "kg_per_box": 15.0
    }
  ]
}
```

---

## 七、错误代码

| 错误代码 | 说明 |
|---------|------|
| INVALID_PARAMETER | 参数错误 |
| RESOURCE_NOT_FOUND | 资源不存在 |
| DUPLICATE_ENTRY | 重复记录 |
| PERMISSION_DENIED | 权限不足 |
| BUSINESS_RULE_VIOLATION | 业务规则违反 |
| DATABASE_ERROR | 数据库错误 |
| INTERNAL_ERROR | 内部错误 |

---

## 八、使用示例

### 8.1 JavaScript (Fetch API)

```javascript
// 创建销售单
async function createSale(saleData) {
  const response = await fetch('/api/sales', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(saleData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error);
  }
  
  return await response.json();
}

// 使用示例
const saleData = {
  customer_id: 1,
  payment_type: 'Crédito',
  items: [
    { spec_id: 1, box_qty: 5, extra_kg: 10.5 }
  ]
};

createSale(saleData)
  .then(sale => console.log('创建成功:', sale))
  .catch(error => console.error('创建失败:', error));
```

### 8.2 Python (requests)

```python
import requests

# 获取销售单列表
def get_sales(page=1, status='active'):
    response = requests.get(
        'http://localhost:5000/api/sales',
        params={'page': page, 'status': status}
    )
    response.raise_for_status()
    return response.json()

# 使用示例
sales = get_sales(page=1, status='active')
print(f"共 {sales['total']} 条记录")
for sale in sales['items']:
    print(f"{sale['id']}: {sale['customer']['name']} - {sale['total_kg']}KG")
```

### 8.3 cURL

```bash
# 创建销售单
curl -X POST http://localhost:5000/api/sales \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "payment_type": "Crédito",
    "items": [
      {"spec_id": 1, "box_qty": 5, "extra_kg": 10.5}
    ]
  }'

# 获取销售单详情
curl http://localhost:5000/api/sales/SALE-20260105-001

# 作废销售单
curl -X POST http://localhost:5000/api/sales/SALE-20260105-001/void \
  -H "Content-Type: application/json" \
  -d '{
    "void_reason": "客户取消订单",
    "void_by": "admin"
  }'
```

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|-----|------|---------|
| 1.0 | 2026-01-05 | 初始版本 |

---

**文档结束**
