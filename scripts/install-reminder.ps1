<#
.SYNOPSIS
  Installs (or removes) the leetcode-mentor daily reminder on Windows.

.DESCRIPTION
  - Registers a per-user notification identity named "LeetCode Mentor" (HKCU only).
  - Creates a per-user scheduled task that runs once a day:
      pythonw mentor.py daily --dir <PracticeDir> --notify
    The task picks today's problem from your progress, refreshes the HTML dashboard,
    and shows the toast. If the laptop was off at that time, it runs at the next start.
  Nothing runs as administrator.

.EXAMPLE
  .\install-reminder.ps1 -PracticeDir D:\leetcode-practice -Time 09:00
.EXAMPLE
  .\install-reminder.ps1 -PracticeDir D:\leetcode-practice -Time 19:30 -Days weekdays
.EXAMPLE
  .\install-reminder.ps1 -Uninstall
#>
param(
    [string]$PracticeDir,
    [string]$Time = '09:00',
    [string]$Days = 'daily',   # 'daily', 'weekdays', or a list like 'Mon,Wed,Fri'
    [switch]$Uninstall,
    [switch]$TestNow
)
$ErrorActionPreference = 'Stop'
$taskName = 'LeetCode Mentor Daily'
$aumid = 'LeetCodeMentor.Reminder'
$regPath = "HKCU:\Software\Classes\AppUserModelId\$aumid"

if ($Uninstall) {
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    if (Test-Path $regPath) { Remove-Item $regPath -Recurse -Force }
    Write-Host 'Removed the daily reminder and the notification identity.'
    return
}

if (-not $PracticeDir) { throw 'Pass -PracticeDir <folder where you run Claude for practice>.' }
$PracticeDir = [System.IO.Path]::GetFullPath($PracticeDir)
New-Item -ItemType Directory -Force $PracticeDir | Out-Null

$script = Join-Path $PSScriptRoot 'mentor.py'
$py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
if (-not $py) {
    $pyExe = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
    if ($pyExe) { $cand = Join-Path (Split-Path $pyExe) 'pythonw.exe'; if (Test-Path $cand) { $py = $cand } else { $py = $pyExe } }
}
if (-not $py) { throw 'Python 3 was not found on PATH. Install it from python.org, then re-run.' }

# 1) Notification identity, so toasts say "LeetCode Mentor" instead of "Windows PowerShell"
$assetDir = Join-Path $env:LOCALAPPDATA 'leetcode-mentor'
New-Item -ItemType Directory -Force $assetDir | Out-Null
New-Item -Path $regPath -Force | Out-Null
New-ItemProperty -Path $regPath -Name DisplayName -Value 'LeetCode Mentor' -PropertyType String -Force | Out-Null
New-ItemProperty -Path $regPath -Name IconUri -Value (Join-Path $assetDir 'logo.png') -PropertyType ExpandString -Force | Out-Null
New-ItemProperty -Path $regPath -Name IconBackgroundColor -Value 'FF7C3AED' -PropertyType String -Force | Out-Null

# 2) Daily scheduled task (current user, no admin)
$at = [datetime]::ParseExact($Time, 'HH:mm', $null)
$action = New-ScheduledTaskAction -Execute $py -Argument "`"$script`" daily --dir `"$PracticeDir`" --notify" -WorkingDirectory $PracticeDir
$dayNames = @{ mon = 'Monday'; tue = 'Tuesday'; wed = 'Wednesday'; thu = 'Thursday'; fri = 'Friday'; sat = 'Saturday'; sun = 'Sunday' }
switch -Regex ($Days.Trim().ToLower()) {
    '^(daily|everyday|all)$' { $trigger = New-ScheduledTaskTrigger -Daily -At $at; $daysLabel = 'every day' }
    '^weekdays?$' {
        $trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At $at
        $daysLabel = 'Mon-Fri'
    }
    default {
        $picked = foreach ($d in ($Days -split '[,\s]+' | Where-Object { $_ })) {
            $k = $d.Substring(0, [Math]::Min(3, $d.Length)).ToLower()
            if (-not $dayNames.ContainsKey($k)) { throw "Unknown day '$d'. Use e.g. -Days 'Mon,Wed,Fri', 'weekdays' or 'daily'." }
            $dayNames[$k]
        }
        $trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek ($picked | Select-Object -Unique) -At $at
        $daysLabel = ($picked | Select-Object -Unique) -join ', '
    }
}
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings `
    -Description 'Picks today''s LeetCode problem from your progress, refreshes the dashboard, and shows a reminder.' -Force | Out-Null

Write-Host "Reminder set for $Time, $daysLabel."
Write-Host "  Practice folder : $PracticeDir"
Write-Host "  Python          : $py"
Write-Host "  Remove later    : .\install-reminder.ps1 -Uninstall"

if ($TestNow) { Start-ScheduledTask -TaskName $taskName; Write-Host 'Sent a test reminder now.' }
