# Restart script for Kardosa application
# Usage: ./restart.ps1

Write-Host "
*** KARDOSA FULL RESTART SCRIPT ***
" -ForegroundColor Green

# Stop all existing Python and Node processes to ensure clean state
Write-Host "Stopping existing processes..." -ForegroundColor Yellow
try {
    Get-Process -Name python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name node* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "All processes stopped successfully" -ForegroundColor Green
} catch {
    Write-Host "Warning: Some processes could not be stopped: $_" -ForegroundColor Yellow
}

# Set up paths
$backendPath = Join-Path $PSScriptRoot "backend"
$frontendPath = Join-Path $PSScriptRoot "frontend"

Write-Host "
Running npm install to ensure dependencies..." -ForegroundColor Cyan
Set-Location -Path $frontendPath
npm install

# Function to open a URL in the default browser
function Open-Browser($url) {
    Start-Process $url
}

# Start Backend Server
Write-Host "
Starting Backend Server (Flask)..." -ForegroundColor Blue
$backendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location -Path $path
    python -m flask run
} -ArgumentList $backendPath

# Wait a moment for backend to initialize
Write-Host "Waiting for backend to initialize..." -ForegroundColor Blue
Start-Sleep -Seconds 3

# Verify backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -Method GET -ErrorAction Stop -TimeoutSec 5
    if($response.StatusCode -eq 200) {
        Write-Host "Backend server running at http://localhost:5000" -ForegroundColor Green
    } else {
        Write-Host "Backend server returned status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Could not connect to backend server: $_" -ForegroundColor Red
    Write-Host "Check backend logs for details" -ForegroundColor Red
}

# Start Frontend Server
Write-Host "
Starting Frontend Server (Next.js)..." -ForegroundColor Magenta
$frontendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location -Path $path
    npm run dev
} -ArgumentList $frontendPath

# Wait for frontend to initialize
Write-Host "Waiting for frontend to initialize..." -ForegroundColor Magenta
Start-Sleep -Seconds 5

# Output running jobs
Write-Host "
Jobs Summary:" -ForegroundColor Cyan
Get-Job | Format-Table -Property Id, Name, State

# Show information about accessing the application
Write-Host "
Application URLs:" -ForegroundColor Green
Write-Host "* Backend API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "* Frontend UI: http://localhost:3000" -ForegroundColor Cyan

Write-Host "
Would you like to open the application in your browser? (Y/N)" -ForegroundColor Yellow
$openBrowser = Read-Host
if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
    Open-Browser "http://localhost:3000"
    Write-Host "Opened http://localhost:3000 in your default browser" -ForegroundColor Green
}

Write-Host "
To stop all servers, run:" -ForegroundColor Red
Write-Host "Get-Job | Remove-Job -Force" -ForegroundColor Red
Write-Host "Get-Process -Name python*,node* | Stop-Process -Force" -ForegroundColor Red

Write-Host "
Application is running! Press Ctrl+C to exit (servers will continue running in background)" -ForegroundColor Green
