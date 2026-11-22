<#
  leetcode-mentor: Windows toast reminder.
  Called by mentor.py with a JSON config. It draws a hero image and shows a
  reminder-style toast with "Solve now", "Progress" and "Snooze" buttons.
  Works in Windows PowerShell 5.1 on Windows 10 and 11. No modules needed.
#>
param(
    [Parameter(Mandatory = $true)][string]$ConfigPath,
    [string]$HeroOut  # if set: only save the card image to this path (no notification)
)

$ErrorActionPreference = 'Stop'
$cfg = Get-Content -Raw -Encoding UTF8 $ConfigPath | ConvertFrom-Json
$assetDir = Join-Path $env:LOCALAPPDATA 'leetcode-mentor'
New-Item -ItemType Directory -Force $assetDir | Out-Null

Add-Type -AssemblyName System.Drawing

function New-RoundedPath([float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
    $p = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = $r * 2
    $p.AddArc($x, $y, $d, $d, 180, 90); $p.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $p.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90); $p.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $p.CloseFigure(); return $p
}

# ---------- hero image (728x360, shown at 364x180) ----------
$W = 728; $H = 360
$bmp = New-Object System.Drawing.Bitmap $W, $H
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = 'AntiAlias'; $g.TextRenderingHint = 'AntiAliasGridFit'
$rect = New-Object System.Drawing.Rectangle 0, 0, $W, $H
$bg = New-Object System.Drawing.Drawing2D.LinearGradientBrush $rect, ([System.Drawing.Color]::FromArgb(255, 76, 29, 149)), ([System.Drawing.Color]::FromArgb(255, 8, 145, 178)), 25
$g.FillRectangle($bg, $rect)
# soft glow circles
$glow = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(40, 255, 255, 255))
$g.FillEllipse($glow, 470, -120, 380, 380); $g.FillEllipse($glow, -140, 210, 320, 320)
# faint code-bracket watermark
$wm = New-Object System.Drawing.Font 'Consolas', 180, ([System.Drawing.FontStyle]::Bold)
$g.DrawString('{ }', $wm, (New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(28, 255, 255, 255))), 400, 40)

$white = [System.Drawing.Brushes]::White
$soft = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(215, 255, 255, 255))
$fEyebrow = New-Object System.Drawing.Font 'Segoe UI Semibold', 17
$fTitle = New-Object System.Drawing.Font 'Segoe UI', 34, ([System.Drawing.FontStyle]::Bold)
$fPill = New-Object System.Drawing.Font 'Segoe UI Semibold', 16
$fStat = New-Object System.Drawing.Font 'Segoe UI', 30, ([System.Drawing.FontStyle]::Bold)
$fStatLbl = New-Object System.Drawing.Font 'Segoe UI', 14

$g.DrawString(("TODAY'S PROBLEM  ·  " + (Get-Date).ToString('ddd dd MMM').ToUpper()), $fEyebrow, $soft, 40, 34)
$titleRect = New-Object System.Drawing.RectangleF 38, 64, 650, 120
$fmt = New-Object System.Drawing.StringFormat; $fmt.Trimming = 'EllipsisWord'
$g.DrawString($cfg.title, $fTitle, $white, $titleRect, $fmt)

# difficulty pill
$pillColor = switch ($cfg.difficulty) { 'Easy' { [System.Drawing.Color]::FromArgb(255, 34, 197, 94) } 'Medium' { [System.Drawing.Color]::FromArgb(255, 245, 158, 11) } default { [System.Drawing.Color]::FromArgb(255, 239, 68, 68) } }
$pw = $g.MeasureString($cfg.difficulty, $fPill).Width + 28
$pp = New-RoundedPath 40 196 $pw 36 18
$g.FillPath((New-Object System.Drawing.SolidBrush $pillColor), $pp)
$g.DrawString($cfg.difficulty, $fPill, $white, 54, 201)
if ($cfg.carried) { $g.DrawString('carried over', $fStatLbl, $soft, (52 + $pw), 204) }

# stat chips
function Draw-Stat($x, $value, $label) {
    $chip = New-RoundedPath $x 256 190 74 16
    $g.FillPath((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(45, 0, 0, 0))), $chip)
    $g.DrawString([string]$value, $fStat, $white, ($x + 14), 258)
    $g.DrawString($label, $fStatLbl, $soft, ($x + 16), 302)
}
Draw-Stat 40 $cfg.streak 'day streak'
Draw-Stat 246 $cfg.due 'revisions due'
$heroPath = Join-Path $assetDir 'toast-hero.png'
$bmp.Save($heroPath, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
if ($HeroOut) { Copy-Item $heroPath $HeroOut -Force; return }

# ---------- app logo (circle, 192x192) ----------
$logoPath = Join-Path $assetDir 'logo.png'
if (-not (Test-Path $logoPath)) {
    $lb = New-Object System.Drawing.Bitmap 192, 192
    $lg = [System.Drawing.Graphics]::FromImage($lb); $lg.SmoothingMode = 'AntiAlias'; $lg.TextRenderingHint = 'AntiAliasGridFit'
    $lr = New-Object System.Drawing.Rectangle 0, 0, 192, 192
    $lbrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush $lr, ([System.Drawing.Color]::FromArgb(255, 124, 58, 237)), ([System.Drawing.Color]::FromArgb(255, 34, 211, 238)), 45
    $lg.FillEllipse($lbrush, $lr)
    $lf = New-Object System.Drawing.Font 'Consolas', 74, ([System.Drawing.FontStyle]::Bold)
    $sf = New-Object System.Drawing.StringFormat; $sf.Alignment = 'Center'; $sf.LineAlignment = 'Center'
    $lg.DrawString('</>', $lf, [System.Drawing.Brushes]::White, (New-Object System.Drawing.RectangleF 0, 4, 192, 192), $sf)
    $lb.Save($logoPath, [System.Drawing.Imaging.ImageFormat]::Png); $lg.Dispose(); $lb.Dispose()
}

# ---------- toast ----------
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

function X([string]$s) { [System.Security.SecurityElement]::Escape($s) }
$line2 = if ($cfg.due -gt 0) { "$($cfg.difficulty) · $($cfg.due) revision(s) due" } else { "$($cfg.difficulty) · no revisions due" }
$heroUri = 'file:///' + ($heroPath -replace '\\', '/')
$logoUri = 'file:///' + ($logoPath -replace '\\', '/')

$xml = @"
<toast activationType="protocol" launch="$(X $cfg.url)" scenario="reminder">
  <visual>
    <binding template="ToastGeneric">
      <text>🔥 $($cfg.streak)-day streak · time to practice</text>
      <text>$(X $cfg.title)</text>
      <text>$(X $line2)</text>
      <text placement="attribution">$(X $cfg.reason)</text>
      <image placement="hero" src="$heroUri"/>
      <image placement="appLogoOverride" hint-crop="circle" src="$logoUri"/>
    </binding>
  </visual>
  <actions>
    <input id="snoozeTime" type="selection" defaultInput="30">
      <selection id="10" content="Remind me in 10 minutes"/>
      <selection id="30" content="Remind me in 30 minutes"/>
      <selection id="60" content="Remind me in 1 hour"/>
      <selection id="180" content="Remind me in 3 hours"/>
    </input>
    <action content="Solve now" activationType="protocol" arguments="$(X $cfg.url)"/>
    <action content="Progress" activationType="protocol" arguments="$(X $cfg.dashboard)"/>
    <action content="Snooze" activationType="system" arguments="snooze" hint-inputId="snoozeTime"/>
  </actions>
  <audio src="ms-winsoundevent:Notification.Reminder"/>
</toast>
"@

$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
$doc.LoadXml($xml)
$toast = New-Object Windows.UI.Notifications.ToastNotification $doc
$toast.Tag = 'daily'; $toast.Group = 'leetcode-mentor'

# Use the registered "LeetCode Mentor" app identity if install-reminder.ps1 created it; otherwise PowerShell's.
$aumid = 'LeetCodeMentor.Reminder'
if (-not (Test-Path "HKCU:\Software\Classes\AppUserModelId\$aumid")) {
    $aumid = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
}
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($aumid).Show($toast)
