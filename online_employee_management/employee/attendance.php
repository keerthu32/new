<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['employee']);
$pageTitle = 'Attendance';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Mark Attendance</h2><p class="muted">Today: <strong><?php echo date('Y-m-d'); ?></strong></p>
<div class="actions"><button class="btn success" type="button">Mark Present</button><button class="btn secondary" type="button">View History</button></div>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
