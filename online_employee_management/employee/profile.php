<?php
require_once __DIR__ . '/../includes/auth.php';
requireRole(['employee']);
$pageTitle = 'My Profile';
include __DIR__ . '/../includes/header.php';
?>
<section class="card"><h2 style="margin-top:0;">Profile</h2>
<form>
<div class="split"><div class="form-group"><label>Name</label><input value="Emma Roberts"></div><div class="form-group"><label>Email</label><input value="emma@company.com"></div></div>
<div class="form-group"><label>Phone</label><input value="+1 555 676 101"></div>
<button class="btn" type="button">Save Changes</button>
</form>
</section>
<?php include __DIR__ . '/../includes/footer.php'; ?>
