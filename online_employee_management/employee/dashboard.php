<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['employee']);
$pageTitle = 'Employee Dashboard';
include __DIR__ . '/../includes/header.php';
?>
<section class="hero"><h1>Employee Dashboard</h1><p>Access your attendance, leave and salary details quickly.</p></section>
<section class="grid">
<article class="card"><h3>Attendance This Month</h3><p class="kpi">95%</p></article>
<article class="card"><h3>Leave Balance</h3><p class="kpi">8</p></article>
<article class="card"><h3>Latest Salary</h3><p class="kpi">$4,300</p></article>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
