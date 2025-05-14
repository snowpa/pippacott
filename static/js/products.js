// 製品管理用JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // データテーブル初期化
  const productsTable = document.getElementById('productsTable');
  if (productsTable && $.fn.DataTable) {
    $(productsTable).DataTable({
      language: {
        url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Japanese.json'
      },
      responsive: true,
      columns: [
        { orderable: true }, // ID
        { orderable: true }, // 製品名
        { orderable: true }, // ベンダー名
        { orderable: true }, // 年間問い合わせ数
        { orderable: false }, // 操作
      ]
    });
  }
  
  // 編集モーダルの処理
  const editProductModal = document.getElementById('editProductModal');
  if (editProductModal) {
    editProductModal.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const productId = button.getAttribute('data-id');
      const productName = button.getAttribute('data-name');
      const productVendor = button.getAttribute('data-vendor');
      const productInquiries = button.getAttribute('data-inquiries');
      
      const modal = this;
      const form = modal.querySelector('form');
      const nameInput = form.querySelector('#editProductName');
      const vendorInput = form.querySelector('#editProductVendor');
      const inquiriesInput = form.querySelector('#editProductInquiries');
      
      nameInput.value = productName;
      vendorInput.value = productVendor;
      inquiriesInput.value = productInquiries;
      
      form.setAttribute('action', `/products/edit/${productId}`);
    });
  }
  
  // ベンダーフィルタリング
  const vendorFilter = document.getElementById('vendorFilter');
  if (vendorFilter && productsTable) {
    // ベンダーのリストを取得してフィルタリングオプションを生成
    const table = $(productsTable).DataTable();
    const vendors = [];
    table.column(2).data().unique().sort().each(function(vendor) {
      vendors.push(vendor);
      const option = document.createElement('option');
      option.value = vendor;
      option.textContent = vendor;
      vendorFilter.appendChild(option);
    });
    
    vendorFilter.addEventListener('change', function() {
      const selectedVendor = this.value;
      
      if (selectedVendor === 'all') {
        table.column(2).search('').draw(); // 全てのベンダーを表示
      } else {
        // 選択したベンダー名と完全一致するものだけをフィルタリング
        table.column(2).search('^' + $.fn.dataTable.util.escapeRegex(selectedVendor) + '$', true, false).draw();
      }
    });
  }
  
  // フォームバリデーション
  const addProductForm = document.getElementById('addProductForm');
  if (addProductForm) {
    addProductForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.classList.add('was-validated');
    });
  }
  
  const editProductForm = document.getElementById('editProductForm');
  if (editProductForm) {
    editProductForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.classList.add('was-validated');
    });
  }
  
  // 問い合わせ数の入力検証
  const inquiriesInputs = document.querySelectorAll('.inquiries-input');
  inquiriesInputs.forEach(function(input) {
    input.addEventListener('input', function() {
      validateNumber(this, 0);
    });
  });
});
