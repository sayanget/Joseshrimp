// 主JavaScript文件

// 工具函数
const utils = {
    // 格式化数字
    formatNumber: (num, decimals = 2) => {
        return parseFloat(num).toFixed(decimals);
    },

    // 显示提示消息
    showAlert: (message, type = 'info') => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);

        // 3秒后自动关闭
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    },

    // API请求封装
    apiRequest: async (url, options = {}) => {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    }
};

// 全局变量
window.utils = utils;

// 主题切换功能
const themeToggle = {
    // 获取当前主题
    getTheme: () => {
        return localStorage.getItem('theme') || 'light';
    },

    // 设置主题
    setTheme: (theme) => {
        const html = document.documentElement;
        const themeIcon = document.getElementById('themeIcon');

        // 添加过渡效果
        html.style.transition = 'background-color 0.3s ease, color 0.3s ease';

        // 设置主题
        html.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);

        // 更新图标
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.className = 'bi bi-sun-fill';
            } else {
                themeIcon.className = 'bi bi-moon-stars';
            }
        }

        // 移除过渡效果（避免影响其他动画）
        setTimeout(() => {
            html.style.transition = '';
        }, 300);
    },

    // 切换主题
    toggle: () => {
        const currentTheme = themeToggle.getTheme();
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        themeToggle.setTheme(newTheme);
    },

    // 初始化
    init: () => {
        // 从localStorage加载主题
        const savedTheme = themeToggle.getTheme();
        themeToggle.setTheme(savedTheme);

        // 绑定切换按钮事件
        const toggleButton = document.getElementById('themeToggle');
        if (toggleButton) {
            toggleButton.addEventListener('click', themeToggle.toggle);
        }
    }
};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 初始化主题
    themeToggle.init();

    // 初始化所有tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // 自动关闭alert
    const alerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});
