// tables.js
// Common functionality for DataTables

document.addEventListener('DOMContentLoaded', function() {
    // Default DataTable configuration
    $.extend(true, $.fn.dataTable.defaults, {
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/ja.json'
        },
        pageLength: 10,
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "すべて"]],
        responsive: true
    });
});
