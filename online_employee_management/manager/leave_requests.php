<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['manager']);
$pageTitle = 'Team Leave Requests';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Team Leave Requests</h2>
<table><thead><tr><th>Employee</th><th>From</th><th>To</th><th>Status</th><th>Action</th></tr></thead>
<tbody><tr><td>Chris Ray</td><td>2026-02-26</td><td>2026-02-27</td><td><span class="badge warning">Pending</span></td><td class="actions"><a class="btn success" href="#">Approve</a><a class="btn danger" href="#">Reject</a></td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
