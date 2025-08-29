# Payroll Application Setup - Run from project directory after cloning

Clear-Host
Write-Host "Setting up Payroll Application..." -ForegroundColor Cyan

# Check PowerShell execution policy
if ((Get-ExecutionPolicy) -eq "Restricted") {
    Write-Host "PowerShell scripts are blocked. Please run this command first:" -ForegroundColor Red
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Docker
try {
    docker --version | Out-Null
    docker info | Out-Null
}
catch {
    Write-Host "Docker Desktop not running. Please:" -ForegroundColor Red
    Write-Host "1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host "2. Start Docker Desktop" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check ports
$ports = @(3002, 8002, 5437)
foreach ($port in $ports) {
    $inUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($inUse) {
        Write-Host "Port $port in use. Run 'docker-compose down' first if app is running." -ForegroundColor Yellow
    }
}

# Start application
Write-Host "Starting containers..." -ForegroundColor Cyan
docker compose down 2>$null
docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start. Check Docker Desktop is running." -ForegroundColor Red
    exit 1
}

# Wait for database
Write-Host "Waiting for database..." -ForegroundColor Cyan
do {
    Start-Sleep 3
    $health = docker inspect --format='{{.State.Health.Status}}' salary_tracker_db 2>$null
} while ($health -ne "healthy")

# Populate data
Write-Host "Adding employees..." -ForegroundColor Cyan
Start-Sleep 5
docker exec -e API_BASE=http://localhost:8000/api salary_tracker_api python add_workers.py

# Success
Write-Host "`nSUCCESS! Application ready at:" -ForegroundColor Green
Write-Host "http://localhost:3002" -ForegroundColor Green
Start-Process "http://localhost:3002"

Read-Host "`nPress Enter to exit"