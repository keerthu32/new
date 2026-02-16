<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['employee']);
$pageTitle = 'Salary Slip';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Salary Slip</h2>
<table><tbody>
<tr><th>Month</th><td>January 2026</td></tr>
<tr><th>Base Salary</th><td>$4,000</td></tr>
<tr><th>Allowance</th><td>$400</td></tr>
<tr><th>Deductions</th><td>$100</td></tr>
<tr><th>Net Salary</th><td><strong>$4,300</strong></td></tr>
</tbody></table>
<div style="margin-top:12px;"><a class="btn secondary" href="#">Download PDF</a></div>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
