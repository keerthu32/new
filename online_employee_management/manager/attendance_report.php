<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['manager']);
$pageTitle = 'Attendance Report';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Team Attendance Report</h2>
<table><thead><tr><th>Employee</th><th>Present Days</th><th>Working Days</th><th>Attendance %</th></tr></thead>
<tbody><tr><td>Emma Roberts</td><td>21</td><td>22</td><td>95.45%</td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
