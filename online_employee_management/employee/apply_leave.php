<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['employee']);
$pageTitle = 'Apply Leave';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Apply for Leave</h2>
<form>
<div class="split"><div class="form-group"><label>From Date</label><input type="date"></div><div class="form-group"><label>To Date</label><input type="date"></div></div>
<div class="form-group"><label>Reason</label><textarea rows="4" placeholder="Enter leave reason..."></textarea></div>
<button class="btn" type="button">Submit Request</button>
</form>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
