// 销售管理页面JavaScript

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('saleForm');
    if (!form) return;

    const customerSelect = document.getElementById('customerId');
    const paymentSelect = document.getElementById('paymentType');
    const creditWarning = document.getElementById('creditWarning');
    const itemsContainer = document.getElementById('itemsContainer');
    const addItemBtn = document.getElementById('addItemBtn');
    const totalKgSpan = document.getElementById('totalKg');

    // 客户选择变化时检查信用
    customerSelect.addEventListener('change', () => {
        const selectedOption = customerSelect.options[customerSelect.selectedIndex];
        const creditAllowed = selectedOption.dataset.credit === 'true';

        if (!creditAllowed && paymentSelect.value === 'Crédito') {
            creditWarning.style.display = 'block';
            paymentSelect.value = '现金';
        } else {
            creditWarning.style.display = 'none';
        }
    });

    // 支付方式变化时检查
    paymentSelect.addEventListener('change', () => {
        const selectedOption = customerSelect.options[customerSelect.selectedIndex];
        const creditAllowed = selectedOption.dataset.credit === 'true';

        if (!creditAllowed && paymentSelect.value === 'Crédito') {
            creditWarning.style.display = 'block';
            paymentSelect.value = '现金';
        } else {
            creditWarning.style.display = 'none';
        }
    });

    // 计算单行小计
    const calculateSubtotal = (row) => {
        const specSelect = row.querySelector('.spec-select');
        const boxQty = parseFloat(row.querySelector('.box-qty').value) || 0;
        const extraKg = parseFloat(row.querySelector('.extra-kg').value) || 0;
        const subtotalInput = row.querySelector('.subtotal-kg');

        const selectedOption = specSelect.options[specSelect.selectedIndex];
        const kgPerBox = parseFloat(selectedOption.dataset.kg) || 0;

        const subtotal = boxQty * kgPerBox + extraKg;
        subtotalInput.value = utils.formatNumber(subtotal, 3);

        calculateTotal();
    };

    // 计算总计
    const calculateTotal = () => {
        let total = 0;
        document.querySelectorAll('.item-row').forEach(row => {
            const subtotal = parseFloat(row.querySelector('.subtotal-kg').value) || 0;
            total += subtotal;
        });
        totalKgSpan.textContent = utils.formatNumber(total, 3);
    };

    // 为所有明细行绑定事件
    const bindItemEvents = (row) => {
        row.querySelector('.spec-select').addEventListener('change', () => calculateSubtotal(row));
        row.querySelector('.box-qty').addEventListener('input', () => calculateSubtotal(row));
        row.querySelector('.extra-kg').addEventListener('input', () => calculateSubtotal(row));

        row.querySelector('.remove-item').addEventListener('click', () => {
            if (document.querySelectorAll('.item-row').length > 1) {
                row.remove();
                calculateTotal();
            } else {
                utils.showAlert('至少需要保留一条明细', 'warning');
            }
        });
    };

    // 初始化第一行
    bindItemEvents(document.querySelector('.item-row'));

    // 添加明细行
    addItemBtn.addEventListener('click', () => {
        const firstRow = document.querySelector('.item-row');
        const newRow = firstRow.cloneNode(true);

        // 清空新行的值
        newRow.querySelector('.product-select').value = '';
        newRow.querySelector('.spec-select').value = '';
        newRow.querySelector('.box-qty').value = '0';
        newRow.querySelector('.extra-kg').value = '0';
        newRow.querySelector('.subtotal-kg').value = '';

        itemsContainer.appendChild(newRow);
        bindItemEvents(newRow);
    });

    // 表单提交
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const customerId = parseInt(customerSelect.value);
        const paymentType = paymentSelect.value;

        if (!customerId) {
            utils.showAlert('请选择客户', 'danger');
            return;
        }

        // 收集明细数据
        const items = [];
        document.querySelectorAll('.item-row').forEach(row => {
            const productId = parseInt(row.querySelector('.product-select').value);
            const specId = parseInt(row.querySelector('.spec-select').value);
            const boxQty = parseInt(row.querySelector('.box-qty').value) || 0;
            const extraKg = parseFloat(row.querySelector('.extra-kg').value) || 0;

            if (productId && specId && (boxQty > 0 || extraKg > 0)) {
                items.push({
                    product_id: productId,
                    spec_id: specId,
                    box_qty: boxQty,
                    extra_kg: extraKg
                });
            }
        });

        if (items.length === 0) {
            utils.showAlert('请至少添加一条有效明细', 'danger');
            return;
        }

        // 提交数据
        try {
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> 创建中...';

            const data = await utils.apiRequest('/api/sales', {
                method: 'POST',
                body: JSON.stringify({
                    customer_id: customerId,
                    payment_type: paymentType,
                    items: items,
                    created_by: 'Jose Burgueno'
                })
            });

            utils.showAlert('销售单创建成功！', 'success');
            setTimeout(() => {
                window.location.href = `/sales/${data.id}`;
            }, 1000);
        } catch (error) {
            utils.showAlert(error.message, 'danger');
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-check-circle"></i> 创建销售单';
        }
    });
});
