#!/usr/bin/env pwsh
# Start new work session - shows project status and helps you pick up where you left off

param(
    [switch]$Quick,
    [string]$Focus = ""
)

Write-Host "`n🚀 CrossPostMe Work Session Startup`n" -ForegroundColor Cyan

# Show current git status
Write-Host "📍 Git Status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Show current branch
$branch = git branch --show-current
Write-Host "🌿 Current Branch: $branch" -ForegroundColor Green
Write-Host ""

# Show recent commits
Write-Host "📝 Recent Commits:" -ForegroundColor Yellow
git log --oneline -5
Write-Host ""

# Check if services are running
Write-Host "🔍 Checking Services..." -ForegroundColor Yellow

# Check backend
$backendRunning = Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*" -or $_.CommandLine -like "*server.py*"}
if ($backendRunning) {
    Write-Host "✅ Backend appears to be running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend not detected - Start with: uvicorn server:app --reload --app-dir .\app\backend" -ForegroundColor Yellow
}

# Check frontend
$frontendRunning = Get-Process | Where-Object {$_.ProcessName -like "*node*" -and $_.CommandLine -like "*react-scripts*"}
if ($frontendRunning) {
    Write-Host "✅ Frontend appears to be running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend not detected - Start with: cd app/frontend && yarn start" -ForegroundColor Yellow
}
Write-Host ""

# Show last session from PROJECT_STATUS.md
Write-Host "📊 Last Known Status:" -ForegroundColor Yellow
if (Test-Path "PROJECT_STATUS.md") {
    # Extract last updated date
    $content = Get-Content "PROJECT_STATUS.md" -Raw
    if ($content -match '\*\*Last Updated:\*\* (.+)') {
        Write-Host "   Last updated: $($matches[1])" -ForegroundColor Gray
    }

    # Check for current focus
    if ($content -match '## 🎯 Current Focus\s+\*\*What we''re working on right now:\*\*\s+- \[ \] (.+)') {
        Write-Host "   Last focus: $($matches[1])" -ForegroundColor Gray
    } else {
        Write-Host "   No current focus set in PROJECT_STATUS.md" -ForegroundColor Gray
    }
} else {
    Write-Host "   PROJECT_STATUS.md not found!" -ForegroundColor Red
}
Write-Host ""

# Check TODO.md
if (Test-Path "app/backend/TODO.md") {
    $todoContent = Get-Content "app/backend/TODO.md" -Raw
    $incompleteTodos = ($todoContent | Select-String -Pattern '- \[ \]' -AllMatches).Matches.Count
    Write-Host "📋 Backend TODO: $incompleteTodos incomplete task(s)" -ForegroundColor Yellow
} else {
    Write-Host "📋 Backend TODO: File not found" -ForegroundColor Yellow
}
Write-Host ""

# Interactive prompts (unless -Quick specified)
if (-not $Quick) {
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "What are you working on this session?" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

    if ($Focus -eq "") {
        $Focus = Read-Host "Enter your focus (or press Enter to skip)"
    }

    if ($Focus -ne "") {
        Write-Host "`n✅ Session focus set: $Focus" -ForegroundColor Green
        Write-Host "💡 Tip: Update PROJECT_STATUS.md with your progress!" -ForegroundColor Cyan
    }
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Quick Commands:" -ForegroundColor Yellow
Write-Host "  📖 Open status:  code PROJECT_STATUS.md" -ForegroundColor Gray
Write-Host "  📋 Open TODO:    code app/backend/TODO.md" -ForegroundColor Gray
Write-Host "  🔧 Start backend: cd app/backend && .\.venv\Scripts\Activate.ps1 && uvicorn server:app --reload" -ForegroundColor Gray
Write-Host "  🎨 Start frontend: cd app/frontend && yarn start" -ForegroundColor Gray
Write-Host "  🐳 Start all:     docker-compose up" -ForegroundColor Gray
Write-Host "  📊 Git log:       git log --oneline --graph -10" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

# Open PROJECT_STATUS.md in default editor if requested
if ($Focus -ne "" -and -not $Quick) {
    $openFile = Read-Host "Open PROJECT_STATUS.md now? (y/n)"
    if ($openFile -eq "y" -or $openFile -eq "Y") {
        code PROJECT_STATUS.md
    }
}
