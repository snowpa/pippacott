// エンジニア管理用JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // データテーブル初期化
  const engineersTable = document.getElementById('engineersTable');
  if (engineersTable && $.fn.DataTable) {
    $(engineersTable).DataTable({
      language: {
        url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Japanese.json'
      },
      responsive: true,
      columns: [
        { orderable: true }, // ID
        { orderable: true }, // 氏名
        { orderable: true }, // 所属部署
        { orderable: false }, // 操作
      ]
    });
  }
  
  // 編集モーダルの処理
  const editEngineerModal = document.getElementById('editEngineerModal');
  if (editEngineerModal) {
    editEngineerModal.addEventListener('show.bs.modal', function(event) {
      const button = event.relatedTarget;
      const engineerId = button.getAttribute('data-id');
      const engineerName = button.getAttribute('data-name');
      const departmentId = button.getAttribute('data-department-id');
      
      const modal = this;
      const form = modal.querySelector('form');
      const nameInput = form.querySelector('#editEngineerName');
      const departmentSelect = form.querySelector('#editEngineerDepartment');
      
      nameInput.value = engineerName;
      departmentSelect.value = departmentId;
      
      form.setAttribute('action', `/engineers/edit/${engineerId}`);
    });
  }
  
  // 部署フィルタリング
  const departmentFilter = document.getElementById('departmentFilter');
  if (departmentFilter && engineersTable) {
    departmentFilter.addEventListener('change', function() {
      const selectedDepartmentId = this.value;
      const table = $(engineersTable).DataTable();
      
      if (selectedDepartmentId === 'all') {
        table.column(2).search('').draw(); // 全ての部署を表示
      } else {
        // 選択した部署名と完全一致するものだけをフィルタリング
        const selectedDepartmentName = this.options[this.selectedIndex].text;
        table.column(2).search('^' + $.fn.dataTable.util.escapeRegex(selectedDepartmentName) + '$', true, false).draw();
      }
    });
  }
  
  // フォームバリデーション
  const addEngineerForm = document.getElementById('addEngineerForm');
  if (addEngineerForm) {
    addEngineerForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.classList.add('was-validated');
    });
  }
  
  const editEngineerForm = document.getElementById('editEngineerForm');
  if (editEngineerForm) {
    editEngineerForm.addEventListener('submit', function(event) {
      if (!this.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.classList.add('was-validated');
    });
  }
});
