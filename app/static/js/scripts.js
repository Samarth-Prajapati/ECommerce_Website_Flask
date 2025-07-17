$(document).ready(function () {
  // Data Table 
    $('#userTable,#productTable,#discountTable,#customerOrdersTable').DataTable();

    $('#downloadReport,#downloadReport1').on('click', function (e) {
        alert('Downloading the full report and sending email...');
    });
  });

// Toast messages
document.addEventListener('DOMContentLoaded', function () {
    const toastElList = document.querySelectorAll('.toast');
    toastElList.forEach(function (toastEl) {
      new bootstrap.Toast(toastEl, { delay: 2000 }).show();
    });
});


