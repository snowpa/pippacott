
document.addEventListener('DOMContentLoaded', function() {
    const grid = new GridJS({
        container: document.getElementById('assignmentGrid'),
        data: window.initialData || [],
        columns: ['エンジニア', ...window.products.map(p => p.name)],
        sort: true,
        search: true,
        pagination: {
            limit: 15
        }
    });

    // ドラッグ&ドロップ機能の初期化
    const cells = document.querySelectorAll('.assignment-cell');
    cells.forEach(cell => {
        cell.addEventListener('dragstart', handleDragStart);
        cell.addEventListener('dragover', handleDragOver);
        cell.addEventListener('drop', handleDrop);
    });

    // リアルタイム更新用WebSocket
    const ws = new WebSocket(`ws://${window.location.host}/ws/assignments`);
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateAssignment(data);
    };

    function updateAssignment(data) {
        const cell = document.querySelector(
            `[data-engineer-id="${data.engineer_id}"][data-product-id="${data.product_id}"]`
        );
        if (cell) {
            cell.dataset.assigned = data.is_assigned ? '1' : '0';
            cell.querySelector('input').checked = data.is_assigned;
            updateCounts();
        }
    }

    function updateCounts() {
        // エンジニアごとの担当数更新
        document.querySelectorAll('tr[data-engineer-id]').forEach(row => {
            const count = row.querySelectorAll('input:checked').length;
            row.querySelector('.product-count').textContent = count;
            row.querySelector('.product-count').dataset.count = count;
        });

        // 製品ごとの担当者数更新
        const productCounts = {};
        document.querySelectorAll('.assignment-cell input:checked').forEach(checkbox => {
            const cell = checkbox.closest('.assignment-cell');
            const productId = cell.dataset.productId;
            productCounts[productId] = (productCounts[productId] || 0) + 1;
        });

        Object.entries(productCounts).forEach(([productId, count]) => {
            const countCell = document.querySelector(`.engineer-count[data-product-id="${productId}"]`);
            if (countCell) {
                countCell.textContent = count;
                countCell.dataset.count = count;
            }
        });

        highlightIssues();
    }
});
