# 🚀 Docker Restart Guide - Fix All Backend Issues

## Problem
After code changes, the Docker containers need to be rebuilt to include the latest fixes for:
- ✅ Login redirect
- ✅ Backend API endpoints
- ✅ Platform integrations
- ✅ AI posting features
- ✅ Analytics tracking
- ✅ Vite installation

---

## Solution: Rebuild Docker Containers

### **Option 1: Using Docker Desktop (Easiest)**

1. **Stop all containers:**
   - Open Docker Desktop
   - Click "Stop" on each container (frontend, backend, mongo, etc.)

2. **Delete containers:**
   - Click the trash icon to delete each stopped container
   - This forces a rebuild on next start

3. **Rebuild from Windows Terminal/PowerShell:**
   ```powershell
   cd C:\Users\johnd\Desktop\CrossPostMe_MR
   docker-compose up --build -d
   ```

---

### **Option 2: Command Line (Complete Clean)**

Open PowerShell/Terminal on your **Windows machine** (not dev container):

```powershell
# Navigate to project directory
cd C:\Users\johnd\Desktop\CrossPostMe_MR

# Pull latest code from GitHub
git pull origin master

# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove all CrossPostMe images to force complete rebuild
docker images | grep crosspostme | awk '{print $3}' | xargs docker rmi -f

# Rebuild everything from scratch (this may take 5-10 minutes)
docker-compose build --no-cache

# Start all services
docker-compose up -d

# View logs to ensure everything started correctly
docker-compose logs -f
```

---

## Verify Everything is Working

### **1. Check Container Status**
```powershell
docker-compose ps
```

You should see:
- ✅ frontend - Up - 0.0.0.0:3000->3000/tcp
- ✅ backend - Up - 0.0.0.0:8000->8000/tcp
- ✅ mongo - Up - 0.0.0.0:27018->27017/tcp
- ✅ grafana - Up - 0.0.0.0:3001->3000/tcp
- ✅ prometheus - Up - 0.0.0.0:9090->9090/tcp

### **2. Test Backend API**

Open your browser and test:

**Backend Health Check:**
```
http://localhost:8000/api/status
```
Expected response: `{"status":"ok","timestamp":"...","db_connected":true}`

**API Documentation:**
```
http://localhost:8000/docs
```
Should show FastAPI interactive documentation

### **3. Test Frontend**
```
http://localhost:3000
```
Should load the homepage

### **4. Test Login Flow**
1. Go to http://localhost:3000/login
2. Click "Try Demo Mode"
3. Should see "Demo login successful! Redirecting..."
4. Should automatically redirect to dashboard

---

## Common Issues & Fixes

### **Issue: Backend shows "Not Found" errors**
**Solution:** Backend needs MongoDB connection. Check:
```powershell
docker-compose logs backend | grep -i mongo
```

### **Issue: Frontend shows "Vite not found"**
**Solution:** Rebuild frontend container:
```powershell
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### **Issue: Can't connect to services**
**Solution:** Ensure ports aren't in use:
```powershell
# Check what's using port 3000
netstat -ano | findstr :3000

# Check what's using port 8000
netstat -ano | findstr :8000
```

### **Issue: MongoDB connection errors**
**Solution:** Reset MongoDB volume:
```powershell
docker-compose down -v
docker volume rm crosspostme_mr_mongo_data
docker-compose up -d
```

---

## What Each Service Does

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **frontend** | 3000 | Vite + React UI | http://localhost:3000 |
| **backend** | 8000 | FastAPI server | http://localhost:8000/api/status |
| **mongo** | 27018 | MongoDB database | docker exec -it crosspostme_mr-mongo-1 mongosh |
| **grafana** | 3001 | Monitoring dashboard | http://localhost:3001 |
| **prometheus** | 9090 | Metrics collection | http://localhost:9090 |

---

## Backend Features That Will Work

After rebuild, all these features will be operational:

### ✅ **Authentication**
- User registration
- Login/Logout
- Demo mode
- **Auto-redirect to dashboard** (just fixed!)

### ✅ **Platform Integrations**
- OAuth for Facebook, eBay, OfferUp
- Credential encryption
- Multi-platform account management

### ✅ **Ad Management**
- Create new listings
- Edit existing ads
- Bulk ad operations
- Image upload

### ✅ **Automation**
- Auto-post to multiple platforms
- Scheduled posting
- Cross-posting workflows

### ✅ **AI Features**
- AI-powered listing generation
- Title optimization
- Description enhancement
- Keyword suggestions

### ✅ **Analytics & Tracking**
- Message inbox
- Lead management
- Response tracking
- Performance metrics
- Email monitoring

---

## Quick Test Commands

```powershell
# Test backend health
curl http://localhost:8000/api/status

# Test frontend
curl http://localhost:3000

# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend

# View all logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# Check MongoDB
docker exec -it crosspostme_mr-mongo-1 mongosh --eval "show dbs"
```

---

## After Rebuild: Test These Features

1. **Login Flow:**
   - Register new account → Auto-login → Redirect to dashboard ✅

2. **Create Ad:**
   - Dashboard → Create Ad → Fill form → Save
   - Should save to database

3. **Platform OAuth:**
   - Settings → Connect Platform → OAuth flow
   - Should store encrypted credentials

4. **AI Generation:**
   - Create Ad → Use AI Assistant → Generate content
   - Should call OpenAI API

5. **Analytics:**
   - Dashboard → View metrics
   - Should show ad performance

---

## Need More Help?

If issues persist after rebuild:

1. **Check container logs:**
   ```powershell
   docker-compose logs backend | tail -100
   ```

2. **Verify environment variables:**
   ```powershell
   docker-compose config
   ```

3. **Test MongoDB connection:**
   ```powershell
   docker exec -it crosspostme_mr-mongo-1 mongosh
   ```

4. **Ensure latest code:**
   ```powershell
   git status
   git pull origin master
   ```

---

**Latest fixes committed:** `ce19689`
**All backend features are in the code - just need Docker rebuild!** 🚀
