<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['employee']);
$pageTitle = 'Leave Status';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">My Leave Requests</h2>
<table><thead><tr><th>Applied On</th><th>From</th><th>To</th><th>Status</th></tr></thead>
<tbody><tr><td>2026-02-10</td><td>2026-02-18</td><td>2026-02-20</td><td><span class="badge warning">Pending</span></td></tr>
<tr><td>2026-01-07</td><td>2026-01-19</td><td>2026-01-19</td><td><span class="badge success">Approved</span></td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
