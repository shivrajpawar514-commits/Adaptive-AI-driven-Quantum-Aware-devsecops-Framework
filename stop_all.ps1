# stop_all.ps1
# Script to stop all running services started by run_all.ps1

$PidFile = Join-Path (Get-Item .).FullName "running_services.json"

if (-not (Test-Path $PidFile)) {
    Write-Host "No PID file found at $PidFile. Are services running?" -ForegroundColor Yellow
    Exit 0
}

$services = Get-Content -Raw -Path $PidFile | ConvertFrom-Json

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Stopping DevSecOps Framework Microservices..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

foreach ($svc in $services) {
    $svcPid = $svc.PID
    $name = $svc.Name
    
    Write-Host "Stopping $name (PID $svcPid)..." -ForegroundColor Green
    try {
        $proc = Get-Process -Id $svcPid -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $svcPid -Force
            Write-Host "  Successfully stopped $name." -ForegroundColor Gray
        } else {
            Write-Host "  Process was already stopped." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  Failed to stop process: $_" -ForegroundColor Red
    }
}

Remove-Item -Path $PidFile -ErrorAction SilentlyContinue
Write-Host "`nAll processes stopped. PID file removed." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
