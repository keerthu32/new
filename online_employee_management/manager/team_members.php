<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['manager']);
$pageTitle = 'Team Members';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">My Team</h2>
<table><thead><tr><th>Name</th><th>Role</th><th>Attendance</th><th>Status</th></tr></thead>
<tbody><tr><td>Emma Roberts</td><td>Software Engineer</td><td>96%</td><td><span class="badge success">Active</span></td></tr>
<tr><td>Chris Ray</td><td>QA Engineer</td><td>91%</td><td><span class="badge success">Active</span></td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
