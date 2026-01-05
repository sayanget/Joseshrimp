# 多语言支持使用说明

## 已实现功能

### 1. 后端支持（Flask-Babel）
- ✅ 安装了 Flask-Babel 4.0.0
- ✅ 配置了三种语言：中文(zh)、英文(en)、西班牙语(es)
- ✅ 实现了语言选择器（优先级：session > URL参数 > 浏览器语言）
- ✅ 创建了语言切换路由 `/language/set-language/<lang>`

### 2. 前端支持（JavaScript i18n）
- ✅ 创建了完整的翻译字典（`i18n.js`）
- ✅ 实现了客户端语言切换功能
- ✅ 支持localStorage持久化语言设置
- ✅ 在导航栏添加了语言切换下拉菜单

### 3. 翻译内容
已翻译的模块：
- 导航栏（首页、销售管理、库存管理、报表统计、系统管理）
- 首页（今日订单、今日销售、现金销售、信用销售、当前库存等）
- 通用术语（查询、添加、编辑、删除、保存、取消等）
- 销售模块（销售单列表、创建销售单、客户、支付方式等）
- 库存模块（当前库存、库存变动、库存盘点）
- 报表模块（按日期统计、按客户统计、按规格统计）

## 使用方法

### 前端使用（推荐）
在HTML元素上添加 `data-i18n` 属性：

```html
<h2 data-i18n="home.title">系统概览</h2>
<button data-i18n="common.search">查询</button>
```

### JavaScript中使用
```javascript
// 获取翻译
const text = window.i18n.t('home.title');

// 切换语言
window.i18n.switchLanguage('en');

// 获取当前语言
const lang = window.i18n.currentLanguage();
```

## 语言切换方式

1. **导航栏下拉菜单**：点击右上角的语言按钮
2. **URL参数**：`?lang=en` 或 `?lang=es`
3. **程序调用**：`switchLanguage('en')`

## 扩展翻译

要添加新的翻译，编辑 `app/static/js/i18n.js`：

```javascript
const translations = {
    zh: {
        'your.key': '你的翻译'
    },
    en: {
        'your.key': 'Your Translation'
    },
    es: {
        'your.key': 'Tu Traducción'
    }
};
```

## 注意事项

1. 当前实现主要基于JavaScript客户端翻译
2. 数据库中的数据（客户名、规格名等）不会被翻译
3. 语言设置保存在localStorage和session中
4. 刷新页面后语言设置会保持

## 下一步优化建议

1. 使用Flask-Babel的模板翻译功能（`{% trans %}...{% endtrans %}`）
2. 提取所有硬编码文本到翻译文件
3. 为API响应消息添加多语言支持
4. 添加更多语言选项
