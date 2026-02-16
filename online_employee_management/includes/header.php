<?php
if (session_status() !== PHP_SESSION_ACTIVE) {
    session_start();
}
$pageTitle = $pageTitle ?? 'Online Employee Management';
$user = $_SESSION['user'] ?? null;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($pageTitle); ?></title>
    <style>
        :root {
            --bg: #f4f7ff;
            --surface: #ffffff;
            --text: #1b2559;
            --muted: #65709a;
            --primary: #3b82f6;
            --primary-700: #2563eb;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: #e4e8f7;
            --shadow: 0 8px 24px rgba(30, 47, 110, .08);
            --radius: 14px;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Inter, Segoe UI, Roboto, Arial, sans-serif;
            background: linear-gradient(180deg, #f8faff 0%, var(--bg) 100%);
            color: var(--text);
        }
        .topbar {
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(255,255,255,.92);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid var(--border);
        }
        .container {
            width: min(1120px, 92%);
            margin: 0 auto;
        }
        .topbar-inner {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 0;
            gap: 12px;
        }
        .brand {
            font-weight: 800;
            letter-spacing: .2px;
            color: var(--primary-700);
            text-decoration: none;
        }
        .nav {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .nav a {
            text-decoration: none;
            color: var(--muted);
            background: #f6f8ff;
            border: 1px solid var(--border);
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 13px;
        }
        .nav a:hover { color: var(--primary-700); border-color: #c9d5ff; }
        main { padding: 24px 0 34px; }
        .hero {
            background: radial-gradient(circle at 10% 10%, #dbeafe 0%, #eff6ff 40%, #fff 100%);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 24px;
            margin-bottom: 18px;
        }
        .hero h1 { margin: 0 0 8px; font-size: clamp(24px, 4vw, 36px); }
        .hero p { margin: 0; color: var(--muted); }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 18px;
        }
        .card h3 { margin-top: 0; margin-bottom: 8px; font-size: 16px; }
        .kpi { font-size: 30px; font-weight: 800; margin: 6px 0 0; }
        .muted { color: var(--muted); }
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
        }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #edf1ff; font-size: 14px; }
        th { background: #f8faff; color: #33417c; }
        .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .btn {
            border: 1px solid transparent;
            background: var(--primary);
            color: #fff;
            padding: 9px 12px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 13px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
        }
        .btn:hover { background: var(--primary-700); }
        .btn.secondary { background: #eef2ff; color: #33417c; border-color: #dbe3ff; }
        .btn.success { background: var(--success); }
        .btn.danger { background: var(--danger); }
        .badge { padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
        .badge.success { background: #dcfce7; color: #166534; }
        .badge.warning { background: #fef3c7; color: #92400e; }
        .badge.danger { background: #fee2e2; color: #991b1b; }
        .form-group { margin-bottom: 14px; }
        label { display: block; margin-bottom: 7px; font-size: 14px; color: #33417c; }
        input, select, textarea {
            width: 100%;
            padding: 10px 11px;
            border-radius: 10px;
            border: 1px solid #dbe3ff;
            font-size: 14px;
        }
        input:focus, select:focus, textarea:focus {
            outline: 2px solid #c4d5ff;
            border-color: #92b1ff;
        }
        .split { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        @media (max-width: 760px) { .split { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
<header class="topbar">
    <div class="container topbar-inner">
        <a class="brand" href="/online_employee_management/index.php">Online Employee Management</a>
        <nav class="nav">
            <?php if ($user): ?>
                <a href="/online_employee_management/<?php echo htmlspecialchars($user['role']); ?>/dashboard.php">Dashboard</a>
                <a href="/online_employee_management/logout.php">Logout</a>
            <?php else: ?>
                <a href="/online_employee_management/login.php">Login</a>
                <a href="/online_employee_management/register.php">Register</a>
            <?php endif; ?>
        </nav>
    </div>
</header>
<main>
    <div class="container">
