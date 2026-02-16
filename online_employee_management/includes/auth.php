<?php
if (session_status() !== PHP_SESSION_ACTIVE) {
    session_start();
}

function requireLogin(): void
{
    if (empty($_SESSION['user'])) {
        header('Location: /online_employee_management/login.php');
        exit;
    }
}

function requireRole(array $roles): void
{
    requireLogin();

    $userRole = $_SESSION['user']['role'] ?? '';
    if (!in_array($userRole, $roles, true)) {
        http_response_code(403);
        echo '<h2>403 - Access denied</h2>';
        exit;
    }
}
