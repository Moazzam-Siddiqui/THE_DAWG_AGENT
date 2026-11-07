$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$launcher = Join-Path $repoRoot "scripts\run_morning.bat"
if (-not (Test-Path $launcher)) { throw "Launcher not found: $launcher" }

$action = New-ScheduledTaskAction -Execute $launcher -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName "TheDawgAgentMorning" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Runs THE DAWG AGENT local Drive-to-Instagram pipeline." -Force
Write-Host "Task registered. Keep this Windows account signed in and the PC awake."
