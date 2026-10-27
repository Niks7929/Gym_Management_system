/**
 * SETFIT GYM ADMIN PANEL - MAIN JAVASCRIPT
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    if (sidebarToggleBtn && sidebar && sidebarBackdrop) {
        sidebarToggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            sidebarBackdrop.classList.toggle('show');
        });

        sidebarBackdrop.addEventListener('click', function () {
            sidebar.classList.remove('show');
            sidebarBackdrop.classList.remove('show');
        });
    }

    // 2. Auto Dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 5000);
    });

    // 3. Print Report Trigger
    const printBtn = document.getElementById('printReportBtn');
    if (printBtn) {
        printBtn.addEventListener('click', function () {
            window.print();
        });
    }

    // 4. Client-side Search / Instant Table Filter (optional booster)
    const instantSearchInputs = document.querySelectorAll('[data-table-search]');
    instantSearchInputs.forEach(input => {
        input.addEventListener('keyup', function () {
            const filterValue = this.value.toLowerCase();
            const targetTableId = this.getAttribute('data-table-search');
            const targetTable = document.getElementById(targetTableId);
            if (!targetTable) return;

            const rows = targetTable.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(filterValue)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
});
