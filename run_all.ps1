# run_all.ps1
# Script to run all 11 microservices and the dashboard frontend locally on Windows (without Docker)

$ErrorActionPreference = "Stop"

$RootPath = (Get-Item .).FullName
$LogsDir = Join-Path $RootPath "logs"
$PidFile = Join-Path $RootPath "running_services.json"

# Check if services are already running according to the PID file
if (Test-Path $PidFile) {
    Write-Host "PID file ($PidFile) already exists." -ForegroundColor Yellow
    Write-Host "Please run .\stop_all.ps1 first to clean up existing processes." -ForegroundColor Red
    Exit 1
}

# Create logs directory
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
    Write-Host "Created logs directory: $LogsDir" -ForegroundColor Green
}

# Resolve python path from local virtual environment
$PythonPath = Join-Path $RootPath ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    Write-Host "Local virtual environment Python not found at: $PythonPath" -ForegroundColor Red
    Write-Host "Please ensure you have created a .venv with the correct dependencies." -ForegroundColor Red
    Exit 1
}

$services = @(
    @{ Name = "Backend Gateway"; Dir = "backend"; Cmd = "node"; Args = "server.js"; Port = 5000 },
    @{ Name = "Monitoring Service"; Dir = "monitoring-service"; Cmd = "node"; Args = "server.js"; Port = 6001 },
    @{ Name = "AI Engine"; Dir = "ai-engine"; Cmd = $PythonPath; Args = "-m uvicorn src.api.main:app --port 8000 --host 127.0.0.1"; Port = 8000 },
    @{ Name = "Cloud Adapter"; Dir = "cloud-adapter"; Cmd = $PythonPath; Args = "-m uvicorn src.main:app --port 7000 --host 127.0.0.1"; Port = 7000 },
    @{ Name = "Risk Engine"; Dir = "risk-engine"; Cmd = $PythonPath; Args = "-m uvicorn src.api.main:app --port 8500 --host 127.0.0.1"; Port = 8500 },
    @{ Name = "Attack Simulator"; Dir = "attack-simulator"; Cmd = $PythonPath; Args = "-m uvicorn src.main:app --port 8600 --host 127.0.0.1"; Port = 8600 },
    @{ Name = "Policy Engine"; Dir = "policy-engine"; Cmd = $PythonPath; Args = "-m uvicorn src.main:app --port 8700 --host 127.0.0.1"; Port = 8700 },
    @{ Name = "Research Evaluator"; Dir = "research-evaluator"; Cmd = $PythonPath; Args = "-m uvicorn src.main:app --port 8800 --host 127.0.0.1"; Port = 8800 },
    @{ Name = "Digital Twin"; Dir = "digital-twin"; Cmd = $PythonPath; Args = "-m uvicorn src.main:app --port 8900 --host 127.0.0.1"; Port = 8900 },
    @{ Name = "Report Generator"; Dir = "report-generator"; Cmd = $PythonPath; Args = "-m uvicorn src.main:app --port 9000 --host 127.0.0.1"; Port = 9000 },
    @{ Name = "Automation Engine"; Dir = "automation-engine"; Cmd = $PythonPath; Args = "-m uvicorn src.main:app --port 9100 --host 127.0.0.1"; Port = 9100 },
    @{ Name = "Dashboard UI"; Dir = "dashboard"; Cmd = "npx.cmd"; Args = "vite --port 5173 --host 127.0.0.1"; Port = 5173 }
)

$runningProcesses = @()

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Starting DevSecOps Framework Microservices... " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

foreach ($svc in $services) {
    $svcName = $svc.Name
    $svcDir = Join-Path $RootPath $svc.Dir
    $svcCmd = $svc.Cmd
    $svcArgs = $svc.Args
    $svcPort = $svc.Port
    
    Write-Host "Starting $svcName on port $svcPort..." -ForegroundColor Green
    
    $stdoutFile = Join-Path $LogsDir "$($svc.Dir).stdout.log"
    $stderrFile = Join-Path $LogsDir "$($svc.Dir).stderr.log"
    
    # Start the process in the background
    $proc = Start-Process -FilePath $svcCmd -ArgumentList $svcArgs -WorkingDirectory $svcDir -NoNewWindow -PassThru -RedirectStandardOutput $stdoutFile -RedirectStandardError $stderrFile
    
    if ($proc) {
        $runningProcesses += @{
            Name = $svcName
            PID  = $proc.Id
            Port = $svcPort
            Dir  = $svc.Dir
        }
        Write-Host "  Started successfully. PID: $($proc.Id)" -ForegroundColor Gray
    } else {
        Write-Host "  FAILED to start $svcName!" -ForegroundColor Red
    }
}

# Save PIDs to file
$runningProcesses | ConvertTo-Json | Out-File -FilePath $PidFile -Encoding utf8
Write-Host "Saved running process details to $PidFile" -ForegroundColor Cyan

Write-Host "`nWaiting 5 seconds for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`nService Ports Status Checking:" -ForegroundColor Cyan
Write-Host "---------------------------------------------" -ForegroundColor Cyan
foreach ($svc in $runningProcesses) {
    $port = $svc.Port
    $name = $svc.Name
    
    # Attempt a TCP connection check on localhost:port
    $tcpConnection = New-Object System.Net.Sockets.TcpClient
    try {
        $tcpConnection.Connect("127.0.0.1", $port)
        Write-Host "  [ONLINE]  $name (Port $port)" -ForegroundColor Green
        $tcpConnection.Close()
    } catch {
        Write-Host "  [OFFLINE] $name (Port $port) - Check logs in logs/$($svc.Dir).stderr.log" -ForegroundColor Red
    }
}

Write-Host "`nAll operations completed! Use stop_all.ps1 to stop all services." -ForegroundColor Green
Write-Host "Dashboard URL: http://localhost:5173" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
