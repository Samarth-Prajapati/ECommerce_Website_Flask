// Toast messages
document.addEventListener('DOMContentLoaded', function () {
    const toastElList = document.querySelectorAll('.toast');
    toastElList.forEach(function (toastEl) {
      new bootstrap.Toast(toastEl, { delay: 2000 }).show();
    });
});

