<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['admin']);
$pageTitle = 'Manage Managers';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Managers</h2><div class="actions" style="margin-bottom:12px;"><button class="btn">+ Add Manager</button></div>
<table><thead><tr><th>Name</th><th>Department</th><th>Team Size</th><th>Actions</th></tr></thead>
<tbody><tr><td>Michael West</td><td>Engineering</td><td>14</td><td class="actions"><a class="btn secondary" href="#">Edit</a><a class="btn danger" href="#">Delete</a></td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
