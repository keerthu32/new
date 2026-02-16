<?php
$pageTitle = 'Register User';
include __DIR__ . '/includes/header.php';
?>
<section class="card" style="max-width:720px; margin: 0 auto;">
    <h2 style="margin-top:0;">Register Manager / Employee</h2>
    <p class="muted">Admin-only action in real deployment. This is a UI scaffold page.</p>
    <form>
        <div class="split">
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" placeholder="e.g. John Carter">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" placeholder="name@company.com">
            </div>
        </div>
        <div class="split">
            <div class="form-group">
                <label>Role</label>
                <select>
                    <option>Manager</option>
                    <option>Employee</option>
                </select>
            </div>
            <div class="form-group">
                <label>Department</label>
                <select>
                    <option>Engineering</option>
                    <option>HR</option>
                    <option>Finance</option>
                </select>
            </div>
        </div>
        <button class="btn" type="button">Create User</button>
    </form>
</section>
<?php include __DIR__ . '/includes/footer.php'; ?>
