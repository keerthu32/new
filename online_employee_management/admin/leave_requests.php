<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['admin']);
$pageTitle = 'Leave Requests';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">All Leave Requests</h2>
<table><thead><tr><th>Employee</th><th>Dates</th><th>Reason</th><th>Status</th><th>Action</th></tr></thead>
<tbody><tr><td>Emma Roberts</td><td>2026-02-18 to 2026-02-20</td><td>Medical</td><td><span class="badge warning">Pending</span></td><td class="actions"><a class="btn success" href="#">Approve</a><a class="btn danger" href="#">Reject</a></td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
