# Redis for Windows Installation Script
Write-Host "Installing Redis for Windows..." -ForegroundColor Green

# Create Redis directory
$redisDir = "C:\redis"
if (!(Test-Path $redisDir)) {
    New-Item -ItemType Directory -Path $redisDir
    Write-Host "Created Redis directory: $redisDir" -ForegroundColor Yellow
}

# Download Redis for Windows
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi"
$redisInstaller = "$env:TEMP\Redis-x64-3.0.504.msi"

Write-Host "Downloading Redis for Windows..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $redisUrl -OutFile $redisInstaller

# Install Redis
Write-Host "Installing Redis..." -ForegroundColor Yellow
Start-Process msiexec.exe -Wait -ArgumentList "/i $redisInstaller /quiet"

# Clean up installer
Remove-Item $redisInstaller -Force

Write-Host "Redis installation completed!" -ForegroundColor Green
Write-Host "Starting Redis service..." -ForegroundColor Yellow

# Start Redis service
Start-Service Redis

Write-Host "Redis is now running on localhost:6379" -ForegroundColor Green
Write-Host "You can now run your FastAPI application!" -ForegroundColor Green 