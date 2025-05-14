// 担当割り当て用JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // 製品テーブルとエンジニアテーブルの初期化
  const assignmentsTable = document.getElementById('assignmentsTable');
  if (assignmentsTable && $.fn.DataTable) {
    const table = $(assignmentsTable).DataTable({
      language: {
        url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Japanese.json'
      },
      responsive: true,
      paging: false,
      columns: [
        { orderable: true }, // ID
        { orderable: true }, // エンジニア名
        { orderable: true }, // 所属部署
        { orderable: true }, // 担当製品数
        { orderable: false }, // 担当製品
      ]
    });
  }
  
  // 製品選択ダイアログの処理
  const productSelectModal = document.getElementById('productSelectModal');
  if (productSelectModal) {
    let currentEngineerId = null;
    let selectedProducts = [];
    
    // 担当製品選択ダイアログを開く処理
    document.querySelectorAll('.select-products-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        const engineerId = this.getAttribute('data-engineer-id');
        const engineerName = this.getAttribute('data-engineer-name');
        const productIds = JSON.parse(this.getAttribute('data-product-ids'));
        
        // 保存用にエンジニアIDを記録
        currentEngineerId = engineerId;
        // 選択済みの製品を記録
        selectedProducts = [...productIds];
        
        // モーダルのタイトルを設定
        productSelectModal.querySelector('.modal-title').textContent = `${engineerName}の担当製品`;
        
        // 全てのチェックボックスの状態をリセット
        productSelectModal.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
          const productId = parseInt(checkbox.value);
          checkbox.checked = selectedProducts.includes(productId);
        });
        
        // 選択数表示を更新
        updateSelectedCount();
        
        // モーダルを表示
        const modal = new bootstrap.Modal(productSelectModal);
        modal.show();
      });
    });
    
    // 製品フィルタリング
    const productFilter = document.getElementById('productFilter');
    if (productFilter) {
      productFilter.addEventListener('input', function() {
        const filterText = this.value.toLowerCase();
        productSelectModal.querySelectorAll('.product-checkbox-wrapper').forEach(function(wrapper) {
          const productName = wrapper.textContent.toLowerCase();
          if (productName.includes(filterText)) {
            wrapper.style.display = '';
          } else {
            wrapper.style.display = 'none';
          }
        });
      });
    }
    
    // 選択済み製品数の表示更新
    function updateSelectedCount() {
      const countElement = document.getElementById('selectedProductsCount');
      if (countElement) {
        countElement.textContent = selectedProducts.length;
      }
    }
    
    // チェックボックスの状態変更時の処理
    productSelectModal.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
      checkbox.addEventListener('change', function() {
        const productId = parseInt(this.value);
        
        if (this.checked) {
          // チェックされた場合、製品IDを追加
          if (!selectedProducts.includes(productId)) {
            selectedProducts.push(productId);
          }
        } else {
          // チェックが外れた場合、製品IDを削除
          const index = selectedProducts.indexOf(productId);
          if (index > -1) {
            selectedProducts.splice(index, 1);
          }
        }
        
        updateSelectedCount();
      });
    });
    
    // 全選択/全解除ボタンの処理
    const selectAllBtn = document.getElementById('selectAllProductsBtn');
    if (selectAllBtn) {
      selectAllBtn.addEventListener('click', function() {
        const checkboxes = productSelectModal.querySelectorAll('input[type="checkbox"]:not([disabled])');
        const visibleCheckboxes = Array.from(checkboxes).filter(checkbox => {
          const wrapper = checkbox.closest('.product-checkbox-wrapper');
          return wrapper.style.display !== 'none';
        });
        
        // 可視状態のチェックボックスが1つでもチェックされていない場合は全選択、そうでなければ全解除
        const someUnchecked = visibleCheckboxes.some(checkbox => !checkbox.checked);
        
        visibleCheckboxes.forEach(function(checkbox) {
          checkbox.checked = someUnchecked;
          
          const productId = parseInt(checkbox.value);
          const index = selectedProducts.indexOf(productId);
          
          if (someUnchecked) {
            // 選択する場合
            if (index === -1) {
              selectedProducts.push(productId);
            }
          } else {
            // 解除する場合
            if (index > -1) {
              selectedProducts.splice(index, 1);
            }
          }
        });
        
        updateSelectedCount();
      });
    }
    
    // 担当製品の保存処理
    const saveProductsBtn = document.getElementById('saveProductsBtn');
    if (saveProductsBtn) {
      saveProductsBtn.addEventListener('click', function() {
        if (currentEngineerId === null) return;
        
        // エンジニアごとの製品IDを更新するために、全エンジニアの現在の割り当て情報を収集
        const assignmentsData = [];
        document.querySelectorAll('.select-products-btn').forEach(function(btn) {
          const engineerId = parseInt(btn.getAttribute('data-engineer-id'));
          let productIds;
          
          if (engineerId === parseInt(currentEngineerId)) {
            // 現在編集中のエンジニアは新しい選択を使用
            productIds = [...selectedProducts];
          } else {
            // それ以外のエンジニアは既存の選択を維持
            productIds = JSON.parse(btn.getAttribute('data-product-ids'));
          }
          
          assignmentsData.push({
            engineerId: engineerId,
            productIds: productIds
          });
        });
        
        // AJAX で割り当て情報を送信
        fetch('/assignments/update', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(assignmentsData)
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // 成功メッセージを表示
            showSuccess(data.message);
            
            // 担当製品数を更新
            const productCountElement = document.querySelector(`tr[data-engineer-id="${currentEngineerId}"] .product-count`);
            if (productCountElement) {
              productCountElement.textContent = selectedProducts.length;
            }
            
            // 担当製品ボタンのdata属性を更新
            const btn = document.querySelector(`.select-products-btn[data-engineer-id="${currentEngineerId}"]`);
            if (btn) {
              btn.setAttribute('data-product-ids', JSON.stringify(selectedProducts));
            }
            
            // モーダルを閉じる
            const modal = bootstrap.Modal.getInstance(productSelectModal);
            modal.hide();
          } else {
            // エラーメッセージを表示
            showError(data.message);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showError('通信エラーが発生しました。再度お試しください。');
        });
      });
    }
  }
  
  // 部署フィルタリング
  const departmentFilter = document.getElementById('assignmentDepartmentFilter');
  if (departmentFilter && assignmentsTable) {
    departmentFilter.addEventListener('change', function() {
      const selectedDepartmentId = this.value;
      const table = $(assignmentsTable).DataTable();
      
      if (selectedDepartmentId === 'all') {
        table.column(2).search('').draw(); // 全ての部署を表示
      } else {
        // 選択した部署名と完全一致するものだけをフィルタリング
        const selectedDepartmentName = this.options[this.selectedIndex].text;
        table.column(2).search('^' + $.fn.dataTable.util.escapeRegex(selectedDepartmentName) + '$', true, false).draw();
      }
    });
  }
});
