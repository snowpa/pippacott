// メインJavaScriptファイル

// サイドバートグル
document.addEventListener('DOMContentLoaded', function() {
  const sidebarToggle = document.getElementById('sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      document.body.classList.toggle('sidebar-toggled');
      document.querySelector('.sidebar').classList.toggle('toggled');
    });
  }
  
  // 小さい画面サイズの場合、サイドバーを自動的に閉じる
  const mediaQuery = window.matchMedia('(max-width: 768px)');
  function handleScreenSizeChange(e) {
    if (e.matches) {
      document.body.classList.add('sidebar-toggled');
      document.querySelector('.sidebar').classList.add('toggled');
    } else {
      document.body.classList.remove('sidebar-toggled');
      document.querySelector('.sidebar').classList.remove('toggled');
    }
  }
  mediaQuery.addEventListener('change', handleScreenSizeChange);
  handleScreenSizeChange(mediaQuery);

  // フラッシュメッセージのトースト表示
  const toastElements = document.querySelectorAll('.toast');
  toastElements.forEach(function(toastEl) {
    const toast = new bootstrap.Toast(toastEl, {
      autohide: true,
      delay: 5000
    });
    toast.show();
  });
  
  // モーダルフォームのリセット処理
  const modals = document.querySelectorAll('.modal');
  modals.forEach(function(modal) {
    modal.addEventListener('hidden.bs.modal', function() {
      const form = modal.querySelector('form');
      if (form) form.reset();
    });
  });
  
  // 編集モーダルの値設定
  document.querySelectorAll('.edit-item-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const itemId = this.getAttribute('data-id');
      const itemData = JSON.parse(this.getAttribute('data-item'));
      const modalId = this.getAttribute('data-bs-target');
      const modal = document.querySelector(modalId);
      
      if (modal) {
        const form = modal.querySelector('form');
        if (form) {
          // フォーム内の入力フィールドに値を設定
          Object.keys(itemData).forEach(function(key) {
            const input = form.elements[key];
            if (input) {
              input.value = itemData[key];
            }
          });
          
          // フォームのaction属性を更新
          const formAction = form.getAttribute('data-edit-action');
          if (formAction) {
            form.setAttribute('action', formAction.replace(':id', itemId));
          }
        }
      }
    });
  });
  
  // データテーブル初期化
  document.querySelectorAll('.datatable').forEach(function(table) {
    if ($.fn.DataTable) {
      $(table).DataTable({
        language: {
          url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Japanese.json'
        },
        responsive: true
      });
    }
  });
});

// 確認ダイアログ
function confirmDelete(event, message) {
  if (!confirm(message || '本当に削除しますか？この操作は取り消せません。')) {
    event.preventDefault();
    return false;
  }
  return true;
}

// 数値入力の検証
function validateNumber(input, min, max) {
  const value = parseFloat(input.value);
  if (isNaN(value)) {
    input.setCustomValidity('数値を入力してください');
  } else if (min !== undefined && value < min) {
    input.setCustomValidity(`${min}以上の値を入力してください`);
  } else if (max !== undefined && value > max) {
    input.setCustomValidity(`${max}以下の値を入力してください`);
  } else {
    input.setCustomValidity('');
  }
  input.reportValidity();
}

// エラーメッセージ表示
function showError(message) {
  const alertDiv = document.createElement('div');
  alertDiv.className = 'alert alert-danger alert-dismissible fade show';
  alertDiv.role = 'alert';
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="閉じる"></button>
  `;
  
  const container = document.querySelector('.container-fluid');
  container.insertBefore(alertDiv, container.firstChild);
  
  // 5秒後に自動的に消える
  setTimeout(() => {
    alertDiv.classList.remove('show');
    setTimeout(() => alertDiv.remove(), 150);
  }, 5000);
}

// 成功メッセージ表示
function showSuccess(message) {
  const alertDiv = document.createElement('div');
  alertDiv.className = 'alert alert-success alert-dismissible fade show';
  alertDiv.role = 'alert';
  alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="閉じる"></button>
  `;
  
  const container = document.querySelector('.container-fluid');
  container.insertBefore(alertDiv, container.firstChild);
  
  // 5秒後に自動的に消える
  setTimeout(() => {
    alertDiv.classList.remove('show');
    setTimeout(() => alertDiv.remove(), 150);
  }, 5000);
}
