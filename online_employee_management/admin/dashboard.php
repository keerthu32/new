<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['admin']);
$pageTitle = 'Admin Dashboard';
include __DIR__ . '/../includes/header.php';
?>
<section class="hero"><h1>Admin Dashboard</h1><p>Organization-wide overview and quick actions.</p></section>
<section class="grid">
  <article class="card"><h3>Total Employees</h3><p class="kpi">124</p></article>
  <article class="card"><h3>Managers</h3><p class="kpi">12</p></article>
  <article class="card"><h3>Pending Leaves</h3><p class="kpi">9</p></article>
  <article class="card"><h3>Payroll This Month</h3><p class="kpi">$84,600</p></article>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
