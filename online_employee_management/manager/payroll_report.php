<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['manager']);
$pageTitle = 'Payroll Report';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Team Payroll Overview</h2>
<table><thead><tr><th>Employee</th><th>Base Salary</th><th>Allowance</th><th>Net Salary</th></tr></thead>
<tbody><tr><td>Emma Roberts</td><td>$4,000</td><td>$400</td><td>$4,300</td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
