<?php
if (session_status() !== PHP_SESSION_ACTIVE) {
    session_start();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $role = $_POST['role'] ?? 'employee';
    $name = trim($_POST['name'] ?? 'User');

    $_SESSION['user'] = [
        'name' => $name !== '' ? $name : 'User',
        'role' => in_array($role, ['admin', 'manager', 'employee'], true) ? $role : 'employee',
    ];

    header('Location: /online_employee_management/' . $_SESSION['user']['role'] . '/dashboard.php');
    exit;
}

$pageTitle = 'Login';
include __DIR__ . '/includes/header.php';
?>
<section class="card" style="max-width:560px; margin: 0 auto;">
    <h2 style="margin-top:0;">Login</h2>
    <p class="muted">Demo login for role-based UI preview.</p>
    <form method="POST">
        <div class="form-group">
            <label>Name</label>
            <input type="text" name="name" placeholder="Enter your name" required>
        </div>
        <div class="form-group">
            <label>Role</label>
            <select name="role">
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="employee" selected>Employee</option>
            </select>
        </div>
        <button class="btn" type="submit">Login</button>
    </form>
</section>
<?php include __DIR__ . '/includes/footer.php'; ?>
