# 🚀 RENDER DEPLOYMENT CONFIGURATION

## Backend Configuration

### Build Command:
```bash
cd app/backend && pip install --upgrade pip && pip install -r requirements.txt
```

### Start Command:
```bash
bash -c "cd app/backend && uvicorn server:app --host 0.0.0.0 --port $PORT"
```

### Alternative Start Command (with Gunicorn for production - RECOMMENDED):
```bash
bash -c "cd app/backend && gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
```

---

## Frontend Configuration

### Build Command:
```bash
cd app/frontend && npm install --legacy-peer-deps && npm run build
```

### Start Command:
```bash
cd app/frontend && npm run preview -- --host 0.0.0.0 --port $PORT
```

### Alternative (using static serve):
```bash
npm install -g serve && cd app/frontend && serve -s dist -l $PORT
```

---

## Environment Variables Needed

### Backend (.env):
```env
# MongoDB
MONGODB_URI=your_mongodb_connection_string

# JWT
JWT_SECRET=your_jwt_secret_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# Platform APIs
EBAY_APP_ID=your_ebay_app_id
EBAY_DEV_ID=your_ebay_dev_id
EBAY_CERT_ID=your_ebay_cert_id

FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

ETSY_API_KEY=your_etsy_api_key
ETSY_SHARED_SECRET=your_etsy_shared_secret

# Frontend URL
FRONTEND_URL=https://your-frontend.onrender.com

# Environment
ENVIRONMENT=production
```

### Frontend (.env):
```env
VITE_API_URL=https://your-backend.onrender.com
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

---

## render.yaml (Complete Configuration)

```yaml
services:
  # Backend Service
  - type: web
    name: crosspostme-backend
    env: python
    region: oregon
    plan: starter
    buildCommand: cd app/backend && pip install --upgrade pip && pip install -r requirements.txt
    startCommand: cd app/backend && gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: MONGODB_URI
        sync: false
      - key: JWT_SECRET
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_PUBLISHABLE_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false
      - key: FRONTEND_URL
        value: https://crosspostme-frontend.onrender.com
      - key: ENVIRONMENT
        value: production
    healthCheckPath: /health

  # Frontend Service
  - type: web
    name: crosspostme-frontend
    env: node
    region: oregon
    plan: starter
    buildCommand: cd app/frontend && npm install --legacy-peer-deps && npm run build
    startCommand: cd app/frontend/dist && npx serve -s . -l $PORT
    envVars:
      - key: NODE_VERSION
        value: 20.10.0
      - key: VITE_API_URL
        value: https://crosspostme-backend.onrender.com
      - key: VITE_STRIPE_PUBLISHABLE_KEY
        sync: false

  # MongoDB (optional - or use MongoDB Atlas)
  # - type: pserv
  #   name: crosspostme-mongodb
  #   env: docker
  #   dockerfilePath: ./Dockerfile.mongo
  #   disk:
  #     name: mongodb-data
  #     mountPath: /data/db
  #     sizeGB: 10
```

---

## Quick Setup Steps

### **1. Create New Web Service (Backend)**
```bash
Service Name: crosspostme-backend
Environment: Python
Build Command: cd app/backend && pip install --upgrade pip && pip install -r requirements.txt
Start Command: bash -c "cd app/backend && gunicorn server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
```

### **2. Create New Web Service (Frontend)**
```bash
Service Name: crosspostme-frontend
Environment: Node
Build Command: cd app/frontend && npm install --legacy-peer-deps && npm run build
Start Command: bash -c "cd app/frontend/dist && npx serve -s . -l $PORT"
```

### 3. Add Environment Variables
- Go to each service settings
- Add all required environment variables
- Save and deploy

---

## backend/requirements.txt (ensure these are included)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pymongo==4.6.0
motor==3.3.2
pydantic==2.5.0
pydantic-settings==2.1.0
stripe==7.8.0
openai==1.3.0
httpx==0.25.2
python-dotenv==1.0.0
```

---

## Frontend package.json (ensure preview script exists)

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "serve": "vite preview --host 0.0.0.0"
  }
}
```

---

## Health Check Endpoint (backend/server.py)

```python
@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    try:
        # Check MongoDB connection
        await db.command('ping')
        return {
            "status": "healthy",
            "service": "crosspostme-backend",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )
```

---

## Deployment Checklist

### Before Deploy:
- [ ] Update CORS origins in backend to include frontend URL
- [ ] Set all environment variables in Render dashboard
- [ ] Ensure MongoDB is accessible (use MongoDB Atlas)
- [ ] Get Stripe keys (test mode for staging)
- [ ] Configure OAuth redirect URIs for production URLs

### After Deploy:
- [ ] Test /health endpoint
- [ ] Test frontend loads
- [ ] Test API connection
- [ ] Test authentication flow
- [ ] Test platform connections
- [ ] Monitor logs for errors

---

## Troubleshooting

### Backend won't start:
```bash
# Check logs for missing dependencies
# Ensure all environment variables are set
# Verify MongoDB connection string
# Check PORT is being used correctly
```

### Frontend won't build:
```bash
# Clear npm cache: npm cache clean --force
# Use --legacy-peer-deps flag
# Check for missing dependencies
# Verify all import paths are correct
```

### CORS errors:
```python
# In backend/server.py, update CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://crosspostme-frontend.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Tips

1. **Use Gunicorn with multiple workers**
   - Handles concurrent requests better
   - Auto-restart on failures

2. **Enable caching**
   - Add Redis for session storage
   - Cache API responses

3. **Optimize builds**
   - Use production builds
   - Minimize bundle sizes
   - Enable compression

4. **Monitor resources**
   - Watch memory usage
   - Check response times
   - Set up alerts

---

## Quick Deploy Commands

### Manual Deploy:
```bash
# Trigger deploy from Render dashboard
# Or push to connected GitHub branch
git add .
git commit -m "Deploy to Render"
git push origin main
```

### Using Render CLI:
```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

---

Ready to deploy! 🚀
