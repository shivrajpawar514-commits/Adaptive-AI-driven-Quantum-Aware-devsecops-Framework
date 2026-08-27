# run_local_framework.ps1
# Script to run all 11 microservices and the dashboard frontend locally on Windows without Docker
# Restored to a simple, reliable background process startup.

param(
    [switch]$Reinstall
)

$ErrorActionPreference = "Continue"

# Define safe unicode character representations to avoid local encoding issues
$CheckMark = [char]0x2714
$CrossMark = [char]0x2716
$WarningSign = [char]0x26A0

$RootPath = (Get-Item .).FullName
$LogsDir = Join-Path $RootPath "logs"
$PidFile = Join-Path $RootPath "running_services.json"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Starting DevSecOps Framework (Local Mode)  " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# ---------------------------------------------------------
# Helper function to test port listening status on both IPv4 & IPv6 loops
# ---------------------------------------------------------
function Test-PortListening {
    param(
        [int]$Port
    )
    
    # Try IPv4 loopback first
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $tcp.Connect("127.0.0.1", $Port)
        $tcp.Close()
        return @{ Success = $true; Host = "127.0.0.1" }
    } catch {}

    # Try IPv6 loopback second
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient([System.Net.Sockets.AddressFamily]::InterNetworkV6)
        $tcp.Connect([System.Net.IPAddress]::IPv6Loopback, $Port)
        $tcp.Close()
        return @{ Success = $true; Host = "[::1]" }
    } catch {}

    return @{ Success = $false; Host = $null }
}

# ---------------------------------------------------------
# Helper function to get PID for a listening port using netstat
# ---------------------------------------------------------
function Get-PidForPort {
    param(
        [int]$Port
    )
    $netstat = netstat -ano 2>$null | Select-String "LISTENING" | Select-String ":$Port\s+"
    if ($netstat) {
        $parts = $netstat.Line.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
        if ($parts.Length -ge 5) {
            return [int]$parts[-1].Trim()
        }
    }
    return $null
}


# ---------------------------------------------------------
# Step 1: Pre-requisites Verification
# ---------------------------------------------------------
Write-Host "[1/4] Verifying pre-requisites..." -ForegroundColor Yellow

# Verify Node.js & npm
try {
    $nodeVer = node -v
    $npmVer = npm -v
    Write-Host "  $CheckMark Node.js: $nodeVer" -ForegroundColor Green
    Write-Host "  $CheckMark npm: $npmVer" -ForegroundColor Green
} catch {
    Write-Host "  $CrossMark Node.js or npm is not installed or not in PATH." -ForegroundColor Red
    Exit 1
}

# Verify Python virtual environment
$PythonPath = Join-Path $RootPath ".venv\Scripts\python.exe"
$PipPath = Join-Path $RootPath ".venv\Scripts\pip.exe"

# ---------------------------------------------------------
# Step 2: Skip Dependency Installation
# ---------------------------------------------------------
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow

# Verify Node dependencies (Existence check only)
$nodeServices = @(
    @{ Name = "Backend Gateway"; Dir = "backend" },
    @{ Name = "Monitoring Service"; Dir = "monitoring-service" },
    @{ Name = "Dashboard UI"; Dir = "dashboard" }
)

foreach ($s in $nodeServices) {
    $nodeModules = Join-Path (Join-Path $RootPath $s.Dir) "node_modules"
    if ($Reinstall -or -not (Test-Path $nodeModules)) {
        Write-Host "  $WarningSign node_modules missing for $($s.Name). Running npm install..." -ForegroundColor Yellow
        Start-Process -FilePath "npm.cmd" -ArgumentList "install" -WorkingDirectory (Join-Path $RootPath $s.Dir) -NoNewWindow -Wait
    } else {
        Write-Host "  $CheckMark Node dependencies exist for $($s.Name) (Skipping install)." -ForegroundColor Green
    }
}

# Verify Python virtual environment & requirements (Existence check only)
if ($Reinstall -or -not (Test-Path $PythonPath)) {
    Write-Host "  $WarningSign Virtual environment missing. Initializing virtual environment..." -ForegroundColor Yellow
    if (-not (Test-Path (Join-Path $RootPath ".venv"))) {
        Start-Process -FilePath "python" -ArgumentList "-m venv .venv" -WorkingDirectory $RootPath -NoNewWindow -Wait
    }
    # Run pip install on all Python services
    $pyServices = @("cloud-adapter", "ai-engine", "risk-engine", "policy-engine", "research-evaluator", "digital-twin", "automation-engine", "attack-simulator", "report-generator", "prediction-engine")
    foreach ($dir in $pyServices) {
        $reqFile = Join-Path (Join-Path $RootPath $dir) "requirements.txt"
        if (Test-Path $reqFile) {
            Write-Host "  Installing python requirements for $dir..." -ForegroundColor Gray
            Start-Process -FilePath $PipPath -ArgumentList "install -r requirements.txt" -WorkingDirectory (Join-Path $RootPath $dir) -NoNewWindow -Wait
        }
    }
} else {
    Write-Host "  $CheckMark Python virtual environment exists (Skipping pip install)." -ForegroundColor Green
}

# Create logs directory
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir | Out-Null
    Write-Host "  $CheckMark Created logs directory: $LogsDir" -ForegroundColor Green
}

# ---------------------------------------------------------
# Step 3: Verify MongoDB Atlas Connectivity
# ---------------------------------------------------------
Write-Host "`n[2/4] Verifying MongoDB Atlas connectivity..." -ForegroundColor Yellow

# Parse MONGO_URI from backend/.env
$backendEnv = Join-Path $RootPath "backend\.env"
$mongoUri = $null

if (Test-Path $backendEnv) {
    $envContent = Get-Content $backendEnv
    foreach ($line in $envContent) {
        if ($line -match "^MONGO_URI=(.+)$") {
            $mongoUri = $Matches[1].Trim()
            break
        }
    }
}

if (-not $mongoUri) {
    Write-Host "  $WarningSign MONGO_URI not found in backend/.env. Using default local Atlas fallback..." -ForegroundColor Yellow
} else {
    Write-Host "  Found MONGO_URI in configuration." -ForegroundColor Gray
}

# Run inline check (zero temporary files on disk, pushing backend node_modules into paths)
$dbConnected = $false
$nodeCode = @"
module.paths.push('backend/node_modules');
const mongoose = require('mongoose');
const uri = process.env.MONGO_URI || '$mongoUri';
if (!uri || uri === 'undefined') {
  console.log('NO_URI');
  process.exit(0);
}
mongoose.connect(uri, { serverSelectionTimeoutMS: 4000 })
  .then(() => {
    console.log('SUCCESS');
    process.exit(0);
  })
  .catch(err => {
    console.log('FAIL: ' + err.message);
    process.exit(1);
  });
"@

$envCommand = if ($mongoUri) { "`$env:MONGO_URI='$mongoUri';" } else { "" }
$output = Invoke-Expression "$envCommand node -e `"$nodeCode`" 2>&1"

if ($output -contains "SUCCESS") {
    Write-Host "  $CheckMark Successfully connected to MongoDB Atlas." -ForegroundColor Green
    $dbConnected = $true
} elseif ($output -contains "NO_URI") {
    Write-Host "  $WarningSign MONGO_URI is empty. Falling back to Mock DB mode." -ForegroundColor Yellow
} else {
    Write-Host "  $WarningSign MongoDB Atlas connection failed: $output" -ForegroundColor Yellow
    Write-Host "  Services will fall back to Mock Database Mode where applicable." -ForegroundColor Yellow
}

# ---------------------------------------------------------
# Step 4: Define Services & Spawn Background PowerShell Processes
# ---------------------------------------------------------
Write-Host "`n[3/4] Spawning services..." -ForegroundColor Yellow

$services = @(
    @{ Name = "Backend Gateway"; Dir = "backend"; Type = "Node"; Port = 5000; TestPath = "/health"; LogName = "backend.log"; Cmd = "npm start" },
    @{ Name = "Monitoring Service"; Dir = "monitoring-service"; Type = "Node"; Port = 6001; TestPath = "/health"; LogName = "monitoring.log"; Cmd = "npm start" },
    @{ Name = "Cloud Adapter"; Dir = "cloud-adapter"; Type = "Python"; Port = 7000; TestPath = "/health"; LogName = "cloud-adapter.log"; Args = "-m uvicorn src.main:app --port 7000 --host 127.0.0.1" },
    @{ Name = "AI Engine"; Dir = "ai-engine"; Type = "Python"; Port = 8000; TestPath = "/health"; LogName = "ai-engine.log"; Args = "-m uvicorn src.api.main:app --port 8000 --host 127.0.0.1" },
    @{ Name = "Risk Engine"; Dir = "risk-engine"; Type = "Python"; Port = 8500; TestPath = "/health"; LogName = "risk-engine.log"; Args = "-m uvicorn src.api.main:app --port 8500 --host 127.0.0.1" },
    @{ Name = "Attack Simulator"; Dir = "attack-simulator"; Type = "Python"; Port = 8600; TestPath = "/health"; LogName = "attack-simulator.log"; Args = "-m uvicorn src.main:app --port 8600 --host 127.0.0.1" },
    @{ Name = "Policy Engine"; Dir = "policy-engine"; Type = "Python"; Port = 8700; TestPath = "/health"; LogName = "policy-engine.log"; Args = "-m uvicorn src.main:app --port 8700 --host 127.0.0.1" },
    @{ Name = "Research Evaluator"; Dir = "research-evaluator"; Type = "Python"; Port = 8800; TestPath = "/health"; LogName = "research-evaluator.log"; Args = "-m uvicorn src.main:app --port 8800 --host 127.0.0.1" },
    @{ Name = "Digital Twin"; Dir = "digital-twin"; Type = "Python"; Port = 8900; TestPath = "/health"; LogName = "digital-twin.log"; Args = "-m uvicorn src.main:app --port 8900 --host 127.0.0.1" },
    @{ Name = "Report Generator"; Dir = "report-generator"; Type = "Python"; Port = 9000; TestPath = "/health"; LogName = "report-generator.log"; Args = "-m uvicorn src.main:app --port 9000 --host 127.0.0.1" },
    @{ Name = "Prediction Engine"; Dir = "prediction-engine"; Type = "Python"; Port = 8005; TestPath = "/health"; LogName = "prediction-engine.log"; Args = "-m uvicorn src.prediction_api:app --port 8005 --host 127.0.0.1" },
    @{ Name = "Automation Engine"; Dir = "automation-engine"; Type = "Python"; Port = 9100; TestPath = "/health"; LogName = "automation-engine.log"; Args = "-m uvicorn src.main:app --port 9100 --host 127.0.0.1" },
    @{ Name = "Dashboard UI"; Dir = "dashboard"; Type = "Node"; Port = 5173; TestPath = "/"; LogName = "dashboard.log"; Cmd = "npm run dev" }
)

# Terminate existing listeners on these ports first
foreach ($svc in $services) {
    $port = $svc.Port
    $badPid = Get-PidForPort -Port $port
    if ($badPid) {
        try {
            taskkill /f /t /pid $badPid 2>$null | Out-Null
        } catch {}
    }
}

# Spawn all processes in parallel in separate background powershell wrapper sessions
foreach ($svc in $services) {
    $svcName = $svc.Name
    $svcDir = Join-Path $RootPath $svc.Dir
    $logFile = Join-Path $LogsDir $svc.LogName

    Remove-Item -Path $logFile -ErrorAction SilentlyContinue

    $cmdLine = ""
    if ($svc.Type -eq "Node") {
        $cmdLine = $svc.Cmd
    } else {
        $cmdLine = "& `"$PythonPath`" $($svc.Args)"
    }

    # Format command for background PowerShell execution
    $powershellCmd = "cd '$svcDir'; $cmdLine > '$logFile' 2>&1"
    
    # Launch background powershell process
    $proc = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile", "-Command", $powershellCmd -WindowStyle Hidden -PassThru
    $svc.WrapperProc = $proc
    $svc.Healthy = $false
    $svc.Host = $null
    $svc.PID = $null
    
    Write-Host "Started background PowerShell process for $svcName." -ForegroundColor Green
}

# ---------------------------------------------------------
# Step 5: Wait and Perform Health Checks
# ---------------------------------------------------------
Write-Host "`nWaiting 15 seconds for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Performing health checks..." -ForegroundColor Yellow

$maxWait = 30
$checkInterval = 2
$elapsed = 0

while ($elapsed -lt $maxWait) {
    $allHealthy = $true
    
    foreach ($svc in $services) {
        if ($svc.Healthy) { continue }
        
        $port = $svc.Port
        $check = Test-PortListening -Port $port
        
        if ($check.Success) {
            $hostToCheck = $check.Host
            
            # Dashboard is ready when port listens
            if ($svc.Name -eq "Dashboard UI") {
                $svc.Healthy = $true
                $svc.Host = $hostToCheck
                $svc.PID = Get-PidForPort -Port $port
                continue
            }
            
            # HTTP Health endpoint query
            $endpoint = "http://$hostToCheck`:$port$($svc.TestPath)"
            try {
                $response = Invoke-WebRequest -Uri $endpoint -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
                if ($response.StatusCode -eq 200 -or ($response.Content -match "status" -or $response.Content -match "Vite" -or $response.Content -match "html")) {
                    $svc.Healthy = $true
                    $svc.Host = $hostToCheck
                    $svc.PID = Get-PidForPort -Port $port
                }
            } catch {}
        }
        
        if (-not $svc.Healthy) {
            $allHealthy = $false
        }
    }
    
    if ($allHealthy) {
        break
    }
    
    Start-Sleep -Seconds $checkInterval
    $elapsed += $checkInterval
}

# ---------------------------------------------------------
# Step 6: Generate Summary and Diagnostics
# ---------------------------------------------------------
Write-Host "`n[4/4] Generating Health Verification Summary..." -ForegroundColor Yellow

Write-Host "`n========================================================================================" -ForegroundColor Cyan
Write-Host "                                   STARTUP SUMMARY                                      " -ForegroundColor Cyan
Write-Host "========================================================================================" -ForegroundColor Cyan

$FormatString = "{0,-10} {1,-22} {2,-6} {3,-8} {4,-35} {5,-20}"
Write-Host ($FormatString -f "Status", "Service", "Port", "PID", "Health URL", "Log Location") -ForegroundColor Cyan
Write-Host ($FormatString -f "------", "-------", "----", "---", "----------", "------------") -ForegroundColor Cyan

$onlineCount = 0
$offlineCount = 0
$runningProcesses = @()

foreach ($svc in $services) {
    $statusChar = if ($svc.Healthy) { "$CheckMark Running" } else { "$CrossMark Failed" }
    $pidVal = if ($svc.PID) { $svc.PID } else { "N/A" }
    $hostVal = if ($svc.Host) { $svc.Host } else { "localhost" }
    $healthUrl = "http://$hostVal`:$($svc.Port)$($svc.TestPath)"
    $logLoc = "logs/$($svc.LogName)"
    
    if ($svc.Healthy) {
        $onlineCount++
        Write-Host ($FormatString -f $statusChar, $svc.Name, $svc.Port, $pidVal, $healthUrl, $logLoc) -ForegroundColor Green
    } else {
        $offlineCount++
        Write-Host ($FormatString -f $statusChar, $svc.Name, $svc.Port, $pidVal, $healthUrl, $logLoc) -ForegroundColor Red
    }
    
    $runningProcesses += [PSCustomObject]@{
        Name    = $svc.Name
        PID     = $svc.PID
        Port    = $svc.Port
        Dir     = $svc.Dir
        Status  = if ($svc.Healthy) { "ONLINE" } else { "OFFLINE" }
        LogName = $svc.LogName
    }
}

Write-Host "========================================================================================" -ForegroundColor Cyan
Write-Host "  Services Online: $onlineCount | Offline: $offlineCount" -ForegroundColor $(if ($offlineCount -gt 0) { "Red" } else { "Green" })
Write-Host "========================================================================================" -ForegroundColor Cyan

# Save PIDs to file for stop_all.ps1 compatibility
$runningProcesses | ConvertTo-Json | Out-File -FilePath $PidFile -Encoding utf8

# Diagnostic logs inspection on failure
$anyFailed = $false
foreach ($svc in $services) {
    if (-not $svc.Healthy) {
        $anyFailed = $true
        Write-Host "`n[DIAGNOSTICS] $($svc.Name) failed to start. Inspecting log file: logs/$($svc.LogName)..." -ForegroundColor Yellow
        $logFile = Join-Path $LogsDir $svc.LogName
        if (Test-Path $logFile) {
            $logLines = Get-Content $logFile -Tail 30 -ErrorAction SilentlyContinue
            Write-Host "Last 30 lines of log:" -ForegroundColor DarkYellow
            foreach ($line in $logLines) {
                Write-Host "    $line" -ForegroundColor Gray
            }
        } else {
            Write-Host "No log file found." -ForegroundColor DarkYellow
        }
    }
}

if (-not $anyFailed) {
    Write-Host "`n✅ Framework Started Successfully`n" -ForegroundColor Green
} else {
    Write-Host "`n[WARNING] Some services failed to start. Please check diagnostics above.`n" -ForegroundColor Yellow
}

# ---------------------------------------------------------
# Keep-alive Crash Monitoring Loop
# ---------------------------------------------------------
Write-Host "[MONITORING] Starting crash monitoring loop. Press Ctrl+C to terminate." -ForegroundColor Yellow

while ($true) {
    Start-Sleep -Seconds 2
    for ($i = 0; $i -lt $runningProcesses.Count; $i++) {
        $svc = $runningProcesses[$i]
        if ($svc.Status -eq "ONLINE") {
            $svcPid = $svc.PID
            $proc = $null
            if ($svcPid -ne $null) {
                $proc = Get-Process -Id $svcPid -ErrorAction SilentlyContinue
            }
            
            # Check process status
            $crashed = $false
            $exitCode = "N/A"
            if ($null -eq $proc -or $proc.HasExited) {
                $crashed = $true
                if ($proc) { $exitCode = $proc.ExitCode }
            } else {
                # Check TCP socket to double check health state
                $check = Test-PortListening -Port $svc.Port
                if (-not $check.Success) {
                    $crashed = $true
                }
            }
            
            if ($crashed) {
                $svc.Status = "CRASHED"
                
                # Fetch last 30 lines of logs
                $logFile = Join-Path $LogsDir $svc.LogName
                $logLines = @()
                if (Test-Path $logFile) {
                    $logLines = Get-Content $logFile -Tail 30 -ErrorAction SilentlyContinue
                }
                
                # Infer error reason from log output
                $reason = "Check logs for details"
                foreach ($line in $logLines) {
                    if ($line -match "Error:|Exception:|failed to|Address already in use|EADDRINUSE|MODULE_NOT_FOUND") {
                        $reason = $line.Trim()
                        break
                    }
                }
                
                Write-Host "`n=============================================" -ForegroundColor Red
                Write-Host "           CRASH DETECTED                    " -ForegroundColor Red
                Write-Host "=============================================" -ForegroundColor Red
                Write-Host "  Service Name: $($svc.Name)" -ForegroundColor Red
                Write-Host "  PID:          $svcPid" -ForegroundColor Red
                Write-Host "  Exit Code:    $exitCode" -ForegroundColor Red
                Write-Host "  Error Reason: $reason" -ForegroundColor Red
                Write-Host "---------------------------------------------" -ForegroundColor Red
                Write-Host "  Last 30 Log Lines:" -ForegroundColor Yellow
                foreach ($line in $logLines) {
                    Write-Host "    $line" -ForegroundColor Gray
                }
                Write-Host "=============================================" -ForegroundColor Red
            }
        }
    }
}
