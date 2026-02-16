<?php
function calculateNetSalary(float $baseSalary, float $allowance = 0.0, float $deduction = 0.0): float
{
    return max(0, $baseSalary + $allowance - $deduction);
}

function getLeaveBalance(int $totalLeaves, int $takenLeaves): int
{
    return max(0, $totalLeaves - $takenLeaves);
}

function attendancePercentage(int $presentDays, int $workingDays): float
{
    if ($workingDays <= 0) {
        return 0;
    }

    return round(($presentDays / $workingDays) * 100, 2);
}
