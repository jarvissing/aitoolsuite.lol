$action = New-ScheduledTaskAction -Execute "C:\Users\admin\.gemini\antigravity\scratch\boring-tool-empire\daily_auto_run.bat" -WorkingDirectory "C:\Users\admin\.gemini\antigravity\scratch\boring-tool-empire"
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "BoringToolEmpire_DailyBot" -Action $action -Trigger $trigger -Settings $settings -Force
Write-Output "Task Scheduler successfully configured with StartWhenAvailable & Battery support!"
