<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['admin']);
$pageTitle = 'Manage Departments';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Departments</h2>
<div class="actions" style="margin-bottom:12px;"><button class="btn">+ Add Department</button></div>
<table><thead><tr><th>Department</th><th>Head</th><th>Employees</th><th>Actions</th></tr></thead>
<tbody><tr><td>Engineering</td><td>Ana Fox</td><td>52</td><td class="actions"><a class="btn secondary" href="#">Edit</a><a class="btn danger" href="#">Delete</a></td></tr>
<tr><td>Human Resources</td><td>David Lin</td><td>11</td><td class="actions"><a class="btn secondary" href="#">Edit</a><a class="btn danger" href="#">Delete</a></td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
