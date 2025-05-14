// 設定画面用JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // タブ切り替え処理
  const settingsTabs = document.querySelectorAll('a[data-bs-toggle="pill"]');
  if (settingsTabs.length > 0) {
    settingsTabs.forEach(function(tab) {
      tab.addEventListener('shown.bs.tab', function(event) {
        // アクティブなタブのIDをURLのハッシュとして設定
        window.location.hash = event.target.getAttribute('href');
      });
    });
    
    // URLのハッシュ値に基づいてタブを選択
    const hash = window.location.hash;
    if (hash) {
      const activeTab = document.querySelector(`a[href="${hash}"]`);
      if (activeTab) {
        const tab = new bootstrap.Tab(activeTab);
        tab.show();
      }
    }
  }
  
  // 設定フォームのバリデーション
  const settingsForm = document.getElementById('settingsForm');
  if (settingsForm) {
    settingsForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.classList.add('was-validated');
    });
    
    // 数値入力のバリデーション
    const minEngineersInput = document.getElementById('min_engineers_per_product');
    if (minEngineersInput) {
      minEngineersInput.addEventListener('input', function() {
        validateNumber(this, 1);
      });
    }
    
    const maxProductsInput = document.getElementById('max_products_per_engineer');
    if (maxProductsInput) {
      maxProductsInput.addEventListener('input', function() {
        validateNumber(this, 1);
      });
    }
    
    const hoursPerInquiryInput = document.getElementById('hours_per_inquiry');
    if (hoursPerInquiryInput) {
      hoursPerInquiryInput.addEventListener('input', function() {
        validateNumber(this, 0.1);
      });
    }
    
    const inquiryWorkRatioInput = document.getElementById('inquiry_work_ratio');
    if (inquiryWorkRatioInput) {
      inquiryWorkRatioInput.addEventListener('input', function() {
        validateNumber(this, 0.01, 1.0);
      });
    }
    
    const workHoursPerDayInput = document.getElementById('work_hours_per_day');
    if (workHoursPerDayInput) {
      workHoursPerDayInput.addEventListener('input', function() {
        validateNumber(this, 0.1);
      });
    }
    
    const workDaysPerYearInput = document.getElementById('work_days_per_year');
    if (workDaysPerYearInput) {
      workDaysPerYearInput.addEventListener('input', function() {
        validateNumber(this, 1);
      });
    }
  }
  
  // 部署フォームのバリデーション
  const departmentForm = document.getElementById('departmentForm');
  if (departmentForm) {
    departmentForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.classList.add('was-validated');
    });
  }
  
  // 部署一覧テーブル
  const departmentsTable = document.getElementById('departmentsTable');
  if (departmentsTable && $.fn.DataTable) {
    $(departmentsTable).DataTable({
      language: {
        url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Japanese.json'
      },
      responsive: true,
      searching: false,
      paging: false,
      info: false,
      columns: [
        { orderable: true }, // ID
        { orderable: true }, // 部署名
        { orderable: false }, // 操作
      ]
    });
  }
  
  // 編集モーダルの処理
  const editDepartmentModal = document.getElementById('editDepartmentModal');
  if (editDepartmentModal) {
    editDepartmentModal.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const departmentId = button.getAttribute('data-id');
      const departmentName = button.getAttribute('data-name');
      
      const modal = this;
      const form = modal.querySelector('form');
      const nameInput = form.querySelector('#editDepartmentName');
      
      nameInput.value = departmentName;
      
      form.setAttribute('action', `/departments/edit/${departmentId}`);
    });
  }
});
