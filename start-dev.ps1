# PowerShell script to start both frontend and backend dev servers automatically
Start-Process -NoNewWindow -FilePath "pwsh" -ArgumentList "-c cd app/backend; uvicorn server:app --reload --host 0.0.0.0 --port 8000" 
Start-Sleep -Seconds 3
Start-Process -NoNewWindow -FilePath "pwsh" -ArgumentList "-c cd app/frontend; yarn start" 
Write-Host "Both backend (port 8000) and frontend (port 3000) are starting..."
