<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['admin']);
$pageTitle = 'Payroll';
include __DIR__ . '/../includes/header.php';
?>
<section class="card">
<h2 style="margin-top:0;">Generate Payroll</h2>
<form class="split">
<div class="form-group"><label>Month</label><input type="month"></div>
<div class="form-group"><label>Department</label><select><option>All</option><option>Engineering</option></select></div>
</form>
<button class="btn success" type="button">Generate</button>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
