#!/usr/bin/env pwsh
# End work session - helps you document what you did and what's next

Write-Host "`n📋 Session Summary Helper`n" -ForegroundColor Cyan

# Show what changed
Write-Host "📝 Files changed this session:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Count uncommitted changes
$changes = git status --short | Measure-Object
$changeCount = $changes.Count

if ($changeCount -gt 0) {
    Write-Host "⚠️  You have $changeCount uncommitted change(s)" -ForegroundColor Yellow
    Write-Host ""

    $commit = Read-Host "Would you like to commit these changes? (y/n)"

    if ($commit -eq "y" -or $commit -eq "Y") {
        Write-Host "`nEnter commit message:" -ForegroundColor Cyan
        $message = Read-Host

        if ($message -ne "") {
            git add -A
            git commit -m $message
            Write-Host "✅ Changes committed!" -ForegroundColor Green

            $push = Read-Host "`nPush to remote? (y/n)"
            if ($push -eq "y" -or $push -eq "Y") {
                git push
                Write-Host "✅ Pushed to remote!" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ Commit cancelled (no message provided)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "✅ No uncommitted changes" -ForegroundColor Green
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Session Wrap-Up Checklist:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# Checklist
$checklist = @(
    "Did you update DAILY_LOG.md with today's work?",
    "Did you update PROJECT_STATUS.md if needed?",
    "Are there any TODOs you should document?",
    "Did you save any important notes or links?",
    "Is there anything you need to remember for next time?"
)

foreach ($item in $checklist) {
    Write-Host "  ☐ $item" -ForegroundColor Gray
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Quick Actions:" -ForegroundColor Yellow
Write-Host "  📖 Open DAILY_LOG:    code DAILY_LOG.md" -ForegroundColor Gray
Write-Host "  📊 Open STATUS:       code PROJECT_STATUS.md" -ForegroundColor Gray
Write-Host "  📋 Open TODO:         code app/backend/TODO.md" -ForegroundColor Gray
Write-Host "  📝 View recent work:  git log --oneline -5" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Write-Host ""
$update = Read-Host "Open DAILY_LOG.md to document this session? (y/n)"
if ($update -eq "y" -or $update -eq "Y") {
    code DAILY_LOG.md
}

Write-Host "`n👋 Session ended. Good work!`n" -ForegroundColor Green
