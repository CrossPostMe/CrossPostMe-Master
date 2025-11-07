# 🔐 Secrets Setup Checklist

Quick checklist to ensure your environment is properly configured for CrossPostMe.

---

## ✅ Initial Setup (First Time)

### Backend Setup

- [ ] Copied `app/backend/.env.example` to `app/backend/.env` (or ran setup script)
- [ ] Generated `SECRET_KEY` with: `openssl rand -hex 32`
- [ ] Generated `JWT_SECRET_KEY` with: `openssl rand -hex 32`
- [ ] Generated `CREDENTIAL_ENCRYPTION_KEY` with Python Fernet
- [ ] Added MongoDB connection string (local or Atlas)
- [ ] Verified MongoDB connection works
- [ ] Obtained eBay API credentials from https://developer.ebay.com/
- [ ] Added eBay credentials to `.env`
- [ ] Obtained Facebook API credentials from https://developers.facebook.com/
- [ ] Added Facebook credentials to `.env`
- [ ] Confirmed `.env` is in `.gitignore`

### Frontend Setup

- [ ] Copied `app/frontend/.env.example` to `app/frontend/.env` (or ran setup script)
- [ ] Set `REACT_APP_API_URL=http://localhost:8000/api`
- [ ] Confirmed `.env` is in `.gitignore`

### Verification

- [ ] Run `git status` - no `.env` files should appear
- [ ] Backend starts successfully: `cd app/backend && uvicorn server:app --reload`
- [ ] Frontend starts successfully: `cd app/frontend && yarn start`
- [ ] Can access backend at http://localhost:8000/api/health
- [ ] Can access frontend at http://localhost:3000
- [ ] No secrets visible in browser console or network tab

---

## 🚀 Production Deployment

### Render (Backend)

- [ ] Created Render account
- [ ] Created Web Service for backend
- [ ] Connected GitHub repository
- [ ] Set branch to `main` (or your production branch)
- [ ] Added all environment variables from `.env.render.example`
- [ ] Generated **new, unique** keys for production (never reuse dev keys!)
- [ ] Added MongoDB Atlas connection string
- [ ] Set `CORS_ORIGINS` to production domain
- [ ] Set `ENVIRONMENT=production`
- [ ] Enabled auto-deploy
- [ ] Verified `/api/health` endpoint responds
- [ ] Checked logs for errors
- [ ] No secrets in logs or error messages

### Hostinger (Frontend) via GitHub Actions

- [ ] Added `HOSTINGER_FTP_SERVER` to GitHub Secrets
- [ ] Added `HOSTINGER_FTP_USERNAME` to GitHub Secrets
- [ ] Added `HOSTINGER_FTP_PASSWORD` to GitHub Secrets
- [ ] Set `REACT_APP_API_URL` to production backend URL
- [ ] Tested workflow manually
- [ ] Verified frontend deployed successfully
- [ ] Frontend can connect to backend API
- [ ] No secrets in built JavaScript files

### MongoDB Atlas

- [ ] Created MongoDB Atlas account
- [ ] Created cluster
- [ ] Created database user with strong password
- [ ] Whitelisted Render IP addresses (or 0.0.0.0/0)
- [ ] Obtained connection string
- [ ] Added connection string to Render environment variables
- [ ] Tested connection from Render backend
- [ ] Enabled MongoDB monitoring/alerts
- [ ] Set up automated backups

---

## 🔄 Regular Maintenance

### Every 90 Days (Minimum)

- [ ] Rotate `SECRET_KEY`
- [ ] Rotate `JWT_SECRET_KEY`
- [ ] Rotate `CREDENTIAL_ENCRYPTION_KEY`
- [ ] Rotate MongoDB password
- [ ] Review eBay API key usage
- [ ] Review Facebook API key usage
- [ ] Update all environments (dev, staging, prod)

### After Any Security Incident

- [ ] Immediately rotate all affected secrets
- [ ] Check git history for leaked secrets
- [ ] Remove secrets from git history if found (use BFG Repo-Cleaner)
- [ ] Notify team members
- [ ] Force push cleaned repository
- [ ] All team members re-clone repository
- [ ] Update all environments with new secrets
- [ ] Monitor for unauthorized access

---

## 🧪 Testing Checklist

### Local Development

- [ ] Backend health check: `curl http://localhost:8000/api/health`
- [ ] MongoDB connection: `python app/backend/check_mongodb.py`
- [ ] Login/auth flow works
- [ ] eBay integration works (if configured)
- [ ] Facebook integration works (if configured)
- [ ] No secrets in console logs

### Production

- [ ] Backend health check: `curl https://www.crosspostme.com/api/health`
- [ ] Frontend loads successfully
- [ ] Login/auth flow works
- [ ] API calls successful (check Network tab)
- [ ] No CORS errors
- [ ] No secrets in browser console
- [ ] No secrets in error messages

---

## 🆘 Troubleshooting

### "SECRET_KEY not found" error

**Solution:**

1. Ensure `.env` file exists in `app/backend/`
2. Run setup script: `./setup-secrets.ps1` or `./setup-secrets.sh`
3. Verify `.env` is not empty

### "MongoDB connection failed"

**Solution:**

1. Check `MONGO_URL` is correct in `.env`
2. For local: ensure MongoDB is running (`mongod`)
3. For Atlas: check IP whitelist and credentials
4. Test with: `node test-mongo.js "your_connection_string"`

### "CORS error" in frontend

**Solution:**

1. Check `CORS_ORIGINS` in backend `.env`
2. Ensure it includes frontend URL
3. Format: `http://localhost:3000,https://www.crosspostme.com` (no spaces)
4. Restart backend after changes

### Git shows .env files

**Solution:**

1. Check `.gitignore` includes `.env` patterns
2. Remove from cache: `git rm --cached app/backend/.env app/frontend/.env`
3. Commit: `git commit -m "Remove .env files from tracking"`

### Secrets visible in build

**Solution:**

1. Frontend: Only use `REACT_APP_*` prefix for safe variables
2. Backend: Never log environment variables
3. Check built files: `grep -r "SECRET_KEY" app/frontend/build/`

---

## 📚 Resources

- **Full Guide:** [SECRETS_MANAGEMENT_GUIDE.md](SECRETS_MANAGEMENT_GUIDE.md)
- **Setup Scripts:**
  - PowerShell: `./setup-secrets.ps1`
  - Bash: `./setup-secrets.sh`
- **Developer Portals:**
  - eBay: https://developer.ebay.com/
  - Facebook: https://developers.facebook.com/
  - MongoDB Atlas: https://cloud.mongodb.com/
  - Render: https://dashboard.render.com/

---

## 🎯 Quick Commands
