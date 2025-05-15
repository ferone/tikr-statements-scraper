# PowerShell script to restart backend and frontend for the stock screener
# Usage: Run this script from the project root in PowerShell

# Use port 8001 instead of 8000 for the backend to avoid port conflicts
$BACKEND_PORT = 8001
$FRONTEND_PORT = 3000

# Function to check if a port is in use
function Test-PortInUse {
    param($port)
    $connections = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | 
                    Where-Object { $_.LocalPort -eq $port }
    return $null -ne $connections
}

# Function to kill process using a specific port
function Kill-ProcessByPort {
    param($port)
    $connections = Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq $port }
    if ($connections) {
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "Killing process $($process.Name) (PID: $($process.Id)) on port $port"
                Stop-Process -Id $process.Id -Force
            }
        }
    }
}

# Output timestamp for logging
Write-Host "===== $(Get-Date) ====="
Write-Host "Starting web application restart process..."

# Kill any running instances first
Write-Host 'Stopping any running processes...'

# Stop processes by name
Write-Host '  Stopping processes by name...'
Get-Process -Name uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*uvicorn*"} | Stop-Process -Force

# Kill processes using our ports
Write-Host '  Stopping processes by port...'
Kill-ProcessByPort -port $BACKEND_PORT
Kill-ProcessByPort -port $FRONTEND_PORT

# Find and stop PowerShell windows hosting our components
Write-Host '  Stopping PowerShell windows hosting our components...'
Get-Process -Name powershell -ErrorAction SilentlyContinue | 
    Where-Object {$_.CommandLine -like "*web-backend*" -or $_.CommandLine -like "*web-frontend*" -or $_.CommandLine -like "*npm start*" -or $_.CommandLine -like "*uvicorn*"} | 
    ForEach-Object {
        Write-Host "    Stopping PowerShell process (PID: $($_.Id))"
        Stop-Process -Id $_.Id -Force
    }

# Verify the ports are free
Write-Host 'Checking if ports are free...'
$backendPortFree = -not (Test-PortInUse -port $BACKEND_PORT)
$frontendPortFree = -not (Test-PortInUse -port $FRONTEND_PORT)

if (-not $backendPortFree) {
    Write-Host "Warning: Port $BACKEND_PORT is still in use. Backend may not start properly." -ForegroundColor Yellow
}
if (-not $frontendPortFree) {
    Write-Host "Warning: Port $FRONTEND_PORT is still in use. Frontend may not start properly." -ForegroundColor Yellow
}

# Update the frontend API URL in .env file
$envFilePath = "web-frontend/.env"
$envContent = @"
REACT_APP_API_BASE=http://localhost:$BACKEND_PORT
"@
Write-Host "Updating frontend API URL to point to port $BACKEND_PORT..."
Set-Content -Path $envFilePath -Value $envContent -Force

# Start backend (FastAPI)
Write-Host "Starting backend (FastAPI) on port $BACKEND_PORT..."
Start-Process powershell -ArgumentList "cd web-backend; .\venv\Scripts\activate; python -m uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT" -WindowStyle Normal

# Wait for backend to be ready
Write-Host 'Waiting for backend to start...'
$retries = 10
$backendReady = $false
for ($i = 0; $i -lt $retries; $i++) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$BACKEND_PORT/fields" -Method Get -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response) {
            $backendReady = $true
            Write-Host "Backend is ready! (after $($i+1) attempts)" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "  Backend not ready yet, waiting... ($($i+1)/$retries)"
    }
}

if (-not $backendReady) {
    Write-Host "Backend might not be ready, but will continue starting frontend." -ForegroundColor Yellow
}

# Start frontend (React)
Write-Host 'Starting frontend (React)...'
Start-Process powershell -ArgumentList 'cd web-frontend; npm start' -WindowStyle Normal

Write-Host @"

Applications started!
=====================
Backend: http://localhost:$BACKEND_PORT
Frontend: http://localhost:$FRONTEND_PORT

To check if backend is working, open: http://localhost:$BACKEND_PORT/docs
"@ -ForegroundColor Cyan 