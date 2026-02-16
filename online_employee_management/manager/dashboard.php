<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['manager']);
$pageTitle = 'Manager Dashboard';
include __DIR__ . '/../includes/header.php';
?>
<section class="hero"><h1>Manager Dashboard</h1><p>Track your team's attendance, payroll and leave status.</p></section>
<section class="grid">
<article class="card"><h3>Team Members</h3><p class="kpi">14</p></article>
<article class="card"><h3>Pending Leaves</h3><p class="kpi">4</p></article>
<article class="card"><h3>Today's Attendance</h3><p class="kpi">92%</p></article>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
