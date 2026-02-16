<?php
$pageTitle = 'Welcome';
include __DIR__ . '/includes/header.php';
?>
<section class="hero">
    <h1>Smart Workforce Management, Simplified</h1>
    <p>Track attendance, manage payroll, and handle leave requests with role-based dashboards for Admin, Manager, and Employee.</p>
    <div style="margin-top:14px;" class="actions">
        <a class="btn" href="/online_employee_management/login.php">Get Started</a>
        <a class="btn secondary" href="/online_employee_management/register.php">Create User</a>
    </div>
</section>

<section class="grid">
    <article class="card"><h3>Admin Controls</h3><p class="muted">Manage departments, employees, managers, payroll, and enterprise-wide reports.</p></article>
    <article class="card"><h3>Manager Workspace</h3><p class="muted">Review team attendance, approve leave requests, and monitor performance insights.</p></article>
    <article class="card"><h3>Employee Self-Service</h3><p class="muted">Mark attendance, apply leave, edit profile, and access salary slips from one place.</p></article>
</section>
<?php include __DIR__ . '/includes/footer.php'; ?>
