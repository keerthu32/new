<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['admin']);
$pageTitle = 'Reports';
include __DIR__ . '/../includes/header.php';
?>
<section class="grid">
<article class="card"><h3>Attendance Report</h3><p class="muted">Monthly attendance trend across departments.</p><a class="btn secondary" href="#">View</a></article>
<article class="card"><h3>Payroll Report</h3><p class="muted">Salary disbursement and deduction summary.</p><a class="btn secondary" href="#">View</a></article>
<article class="card"><h3>Leave Report</h3><p class="muted">Leave utilization and pending approvals.</p><a class="btn secondary" href="#">View</a></article>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
