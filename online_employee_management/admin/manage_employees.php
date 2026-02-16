<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['admin']);
$pageTitle = 'Manage Employees';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Employees</h2><div class="actions" style="margin-bottom:12px;"><button class="btn">+ Add Employee</button></div>
<table><thead><tr><th>Name</th><th>Department</th><th>Manager</th><th>Status</th><th>Actions</th></tr></thead>
<tbody><tr><td>Emma Roberts</td><td>Engineering</td><td>Michael West</td><td><span class="badge success">Active</span></td><td class="actions"><a class="btn secondary" href="#">Edit</a><a class="btn danger" href="#">Remove</a></td></tr>
<tr><td>Tom Hardy</td><td>Finance</td><td>Nina Patel</td><td><span class="badge warning">Probation</span></td><td class="actions"><a class="btn secondary" href="#">Edit</a><a class="btn danger" href="#">Remove</a></td></tr></tbody></table>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
