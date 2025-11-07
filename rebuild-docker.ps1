# CrossPostMe Docker Rebuild Script
# Run this from PowerShell on your Windows machine

Write-Host "🚀 CrossPostMe - Docker Rebuild Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
$projectPath = "C:\Users\johnd\Desktop\CrossPostMe_MR"
Write-Host "📁 Navigating to project directory..." -ForegroundColor Yellow
cd $projectPath

# Pull latest code
Write-Host "📥 Pulling latest code from GitHub..." -ForegroundColor Yellow
git pull origin master

# Stop and remove containers
Write-Host "🛑 Stopping all containers..." -ForegroundColor Yellow
docker-compose down -v

# Rebuild containers
Write-Host "🔨 Rebuilding containers (this may take 5-10 minutes)..." -ForegroundColor Yellow
docker-compose build --no-cache

# Start services
Write-Host "▶️  Starting all services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to start
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
Write-Host ""
Write-Host "✅ Container Status:" -ForegroundColor Green
docker-compose ps

Write-Host ""
Write-Host "🌐 Testing services..." -ForegroundColor Yellow

# Test backend
$backendHealth = try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/status" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) { "✅ HEALTHY" } else { "❌ ERROR" }
} catch { "❌ NOT ACCESSIBLE" }

Write-Host "   Backend (8000): $backendHealth"

# Test frontend
$frontendHealth = try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) { "✅ HEALTHY" } else { "❌ ERROR" }
} catch { "❌ NOT ACCESSIBLE" }

Write-Host "   Frontend (3000): $frontendHealth"

Write-Host ""
Write-Host "🎉 Done! Access your application at:" -ForegroundColor Green
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Grafana: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 To view logs, run: docker-compose logs -f" -ForegroundColor Yellow
Write-Host ""
