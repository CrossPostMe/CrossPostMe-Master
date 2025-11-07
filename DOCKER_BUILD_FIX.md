# Docker Build Error Fix: "invalid file request .venv/bin/python"

## Problem
Docker is trying to copy `.venv/` directory even though it's in `.dockerignore`.

## Solution

### Option 1: Clean Build (Recommended)

On your Windows machine in PowerShell:

```powershell
cd C:\Users\johnd\Desktop\CrossPostMe_MR

# Pull latest code
git pull origin master

# Stop all containers
docker-compose down

# Remove all images and build cache
docker system prune -a --volumes -f

# Rebuild from scratch
docker-compose build --no-cache

# Start services
docker-compose up -d
```

### Option 2: Quick Fix - Remove .venv Locally

```powershell
cd C:\Users\johnd\Desktop\CrossPostMe_MR

# Remove .venv from backend (it will be recreated if needed)
Remove-Item -Recurse -Force .\app\backend\.venv -ErrorAction SilentlyContinue

# Now rebuild
docker-compose build --no-cache backend
docker-compose up -d
```

### Option 3: Build from Specific Context

If the above doesn't work, the issue might be the build context. Modify your build command:

```powershell
# Build backend with explicit context
cd C:\Users\johnd\Desktop\CrossPostMe_MR\app\backend
docker build --no-cache -t crosspostme_mr-backend .

# Then start with docker-compose
cd C:\Users\johnd\Desktop\CrossPostMe_MR
docker-compose up -d
```

## Why This Happens

The `.venv` directory is a Python virtual environment that gets created when you run:
```bash
python -m venv .venv
```

Docker should ignore it via `.dockerignore`, but sometimes:
1. Build cache has old references
2. The file was added before `.dockerignore` was updated
3. Docker context includes symlinks or mounted volumes

## Prevention

Make sure `.venv/` is in both:
1. `.gitignore` (already is)
2. `.dockerignore` (already is)

Never commit `.venv/` to git!

## Verify Fix

After rebuild, check that backend starts without errors:

```powershell
# Check logs
docker-compose logs backend

# Should see:
# INFO: Uvicorn running on http://0.0.0.0:8000
# INFO: Application startup complete
```

Test the metrics endpoint:
```powershell
curl http://localhost:8000/metrics
```

Should return Prometheus metrics (not 404).
