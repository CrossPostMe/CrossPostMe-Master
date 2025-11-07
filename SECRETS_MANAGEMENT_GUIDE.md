# 🔐 Secrets Management Guide

**Complete guide to managing environment variables and secrets for CrossPostMe**

---

## 🎯 Quick Answer: Where to Store Secrets

| Environment    | Backend Secrets           | Frontend Config         | MongoDB Credentials              |
| -------------- | ------------------------- | ----------------------- | -------------------------------- |
| **Local Dev**  | `app/backend/.env`        | `app/frontend/.env`     | Local in both .env files         |
| **Production** | **Render** Dashboard      | **GitHub Secrets**      | **MongoDB Atlas** + Render       |
| **Staging**    | Render (separate service) | GitHub Secrets (branch) | MongoDB Atlas (separate cluster) |

**Golden Rule:** Never commit `.env` files to git. Always use `.env.example` templates.

---

## 📁 File Structure

```
CrossPostMe_MR/
├── app/
│   ├── backend/
│   │   ├── .env                 # ❌ Git-ignored (YOUR secrets)
│   │   ├── .env.example         # ✅ Git-committed (template)
│   │   ├── .env.render          # ❌ Git-ignored (Render-specific)
│   │   └── .env.testing         # ❌ Git-ignored (for tests)
│   │
│   └── frontend/
│       ├── .env                 # ❌ Git-ignored (YOUR config)
│       ├── .env.example         # ✅ Git-committed (template)
│       ├── .env.local           # ❌ Git-ignored (local overrides)
│       └── .env.production      # ❌ Git-ignored (production build)
│
└── SECRETS_MANAGEMENT_GUIDE.md  # ✅ This file
```

---

## 🔑 1. Backend Environment Variables

### File: `app/backend/.env`

```bash
# ============================================================================
# BACKEND SECRETS - NEVER COMMIT THIS FILE
# ============================================================================

# ----- Authentication & Security -----
SECRET_KEY=<generate_with_openssl_rand_hex_32>
JWT_SECRET_KEY=<generate_with_openssl_rand_hex_32>
CREDENTIAL_ENCRYPTION_KEY=<generate_with_python_fernet>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ----- Database -----
MONGO_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DB_NAME=crosspostme
MONGO_SERVER_SELECTION_TIMEOUT_MS=15000

# ----- CORS (comma-separated) -----
CORS_ORIGINS=http://localhost:3000,https://www.crosspostme.com

# ----- Platform API Keys -----
EBAY_APP_ID=<from_ebay_developer_portal>
EBAY_CERT_ID=<from_ebay_developer_portal>
EBAY_DEV_ID=<from_ebay_developer_portal>

FACEBOOK_APP_ID=<from_facebook_developers>
FACEBOOK_APP_SECRET=<from_facebook_developers>
FACEBOOK_DOWNLOAD_TIMEOUT=120
FACEBOOK_UPLOAD_TIMEOUT=120

# ----- Optional Monitoring -----
SENTRY_DSN=<optional_sentry_dsn_for_error_tracking>

# ----- Environment -----
ENVIRONMENT=development  # development, staging, production
```

### How to Generate Keys

```powershell
# SECRET_KEY and JWT_SECRET_KEY
openssl rand -hex 32

# CREDENTIAL_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🎨 2. Frontend Environment Variables

### File: `app/frontend/.env`

```bash
# ============================================================================
# FRONTEND CONFIG - NEVER COMMIT THIS FILE
# ============================================================================

# ----- API Configuration -----
REACT_APP_API_URL=http://localhost:8000/api

# ----- Environment -----
REACT_APP_ENV=development  # development, staging, production

# ----- Feature Flags (optional) -----
REACT_APP_ENABLE_AUTH=true
REACT_APP_ENABLE_FACEBOOK=true
REACT_APP_ENABLE_EBAY=true

# ----- Analytics (optional) -----
REACT_APP_GA_TRACKING_ID=<google_analytics_id_optional>

# ----- Sentry (optional) -----
REACT_APP_SENTRY_DSN=<sentry_dsn_for_frontend_optional>
```

### Environment-Specific Variants

**Local Development:**

```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```

**Production:**

```bash
REACT_APP_API_URL=https://www.crosspostme.com/api
REACT_APP_ENV=production
```

---

## 🌐 3. Where to Store Secrets by Platform

### Local Development

**Backend:**

1. Copy template: `cp app/backend/.env.example app/backend/.env`
2. Generate keys (see commands above)
3. Add your MongoDB connection string
4. Add platform API keys from developer portals

**Frontend:**

1. Copy template: `cp app/frontend/.env.example app/frontend/.env`
2. Set `REACT_APP_API_URL=http://localhost:8000/api`

---

### Production: Render (Backend)

**Where:** Render Dashboard → Your Service → Environment

**How to add secrets:**

1. Go to https://dashboard.render.com
2. Select your backend service
3. Navigate to "Environment" tab
4. Add each variable as Key-Value pair
5. Click "Save Changes"

**Required secrets in Render:**

```
SECRET_KEY=<your_generated_key>
JWT_SECRET_KEY=<your_generated_key>
CREDENTIAL_ENCRYPTION_KEY=<your_generated_key>
MONGO_URL=<mongodb_atlas_connection_string>
DB_NAME=crosspostme
CORS_ORIGINS=https://www.crosspostme.com
EBAY_APP_ID=<your_ebay_app_id>
EBAY_CERT_ID=<your_ebay_cert_id>
EBAY_DEV_ID=<your_ebay_dev_id>
FACEBOOK_APP_ID=<your_facebook_app_id>
FACEBOOK_APP_SECRET=<your_facebook_app_secret>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
MONGO_SERVER_SELECTION_TIMEOUT_MS=15000
ENVIRONMENT=production
```

**Tips:**

- Use "Add Secret File" for multi-line secrets
- Click the lock icon to mark sensitive values
- Changes trigger automatic redeployment

---

### Production: GitHub Secrets (Frontend)

**Where:** GitHub → Repository → Settings → Secrets and Variables → Actions

**How to add secrets:**

1. Go to your GitHub repository
2. Settings → Secrets and Variables → Actions
3. Click "New repository secret"
4. Add each secret
5. Use in workflows with `${{ secrets.SECRET_NAME }}`

**Required secrets in GitHub:**

```
HOSTINGER_FTP_SERVER=<ftp_server_address>
HOSTINGER_FTP_USERNAME=<username>
HOSTINGER_FTP_PASSWORD=<password>
REACT_APP_API_URL=https://www.crosspostme.com/api
```

**Example workflow usage:**

```yaml
- name: Deploy to Hostinger
  env:
    REACT_APP_API_URL: ${{ secrets.REACT_APP_API_URL }}
    REACT_APP_ENV: production
  run: yarn build && ./scripts/deploy.sh
```

---

### Production: MongoDB Atlas

**Where:** MongoDB Atlas Dashboard → Database Access & Network Access

**How to set up:**

1. Go to https://cloud.mongodb.com
2. Create a database user:
   - Database Access → Add New Database User
   - Username: `crosspostme-app`
   - Password: Generate strong password
   - Role: Read and write to any database
3. Whitelist IP addresses:
   - Network Access → Add IP Address
   - For Render: Add Render's IP ranges or use `0.0.0.0/0` (less secure)
4. Get connection string:
   - Clusters → Connect → Connect your application
   - Copy the connection string
   - Replace `<password>` with actual password

**Connection string format:**

```
mongodb+srv://crosspostme-app:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

---

## 🔒 4. Security Best Practices

### ✅ DO

- **Use `.env.example` templates** - Commit examples, never real secrets
- **Generate unique keys per environment** - Different keys for dev/staging/prod
- **Rotate secrets regularly** - Every 90 days minimum
- **Use strong, random keys** - Use `openssl rand` or Fernet
- **Restrict access** - Only grant secrets to people/services that need them
- **Use MongoDB IP whitelisting** - Restrict to specific IPs when possible
- **Enable MongoDB authentication** - Always use username/password
- **Use HTTPS in production** - Never send secrets over HTTP
- **Monitor for leaked secrets** - Use tools like GitGuardian or TruffleHog
- **Document required secrets** - Keep this guide updated

### ❌ DON'T

- **Never commit `.env` files** - Add to `.gitignore`
- **Never hardcode secrets in code** - Always use environment variables
- **Never share secrets in chat/email** - Use secure sharing tools
- **Never use weak passwords** - Don't use "password123"
- **Never expose secrets in logs** - Sanitize log output
- **Never use production secrets in dev** - Keep environments separate
- **Never commit secrets to git history** - If you do, rotate immediately
- **Never use the same key for multiple purposes** - Separate keys for JWT, encryption, etc.

---

## 🚨 5. Emergency: Secrets Leaked

**If secrets are committed to git:**

1. **Immediately rotate all exposed secrets:**
   - Generate new keys
   - Update in all environments
   - Revoke old credentials from third-party services

2. **Remove from git history:**

   ```powershell
   # Option 1: BFG Repo-Cleaner (fastest)
   git clone --mirror your-repo.git
   java -jar bfg.jar --delete-files .env your-repo.git
   cd your-repo.git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force

   # Option 2: git-filter-repo
   git filter-repo --path app/backend/.env --invert-paths
   git push --force
   ```

3. **Notify team members:**
   - Everyone must re-clone the repository
   - Update their local `.env` files with new secrets

4. **Verify removal:**
   - Check GitHub history
   - Search for exposed values in code

---

## 📋 6. Secrets Checklist by Environment

### Local Development Setup

```
[ ] Copied .env.example to .env for backend
[ ] Generated SECRET_KEY with openssl
[ ] Generated JWT_SECRET_KEY with openssl
[ ] Generated CREDENTIAL_ENCRYPTION_KEY with Fernet
[ ] Added MongoDB connection string (local or Atlas)
[ ] Added eBay API credentials
[ ] Added Facebook API credentials
[ ] Copied .env.example to .env for frontend
[ ] Set REACT_APP_API_URL to http://localhost:8000/api
[ ] Verified .env files are in .gitignore
[ ] Can start backend successfully
[ ] Can start frontend successfully
[ ] Can connect to MongoDB
```

### Production Setup (Render)

```
[ ] Added all backend secrets to Render Environment
[ ] Verified MongoDB connection string is correct
[ ] Verified CORS_ORIGINS includes production domain
[ ] Set ENVIRONMENT=production
[ ] Enabled Render auto-deploy from main branch
[ ] Tested /api/health endpoint
[ ] Tested /api/ready endpoint
[ ] Verified logs show no secret leaks
```

### Production Setup (Frontend)

```
[ ] Added HOSTINGER_FTP_* secrets to GitHub Secrets
[ ] Added REACT_APP_API_URL to GitHub Secrets (or build config)
[ ] Verified deploy workflow uses secrets correctly
[ ] Tested production build locally
[ ] Verified frontend can connect to backend API
[ ] Checked browser console for errors
[ ] Verified no secrets in built JavaScript files
```

### MongoDB Atlas Setup

```
[ ] Created database user with strong password
[ ] Whitelisted application IPs (or 0.0.0.0/0)
[ ] Copied connection string
[ ] Replaced <password> in connection string
[ ] Added connection string to Render
[ ] Tested connection with test-mongo.js
[ ] Enabled MongoDB monitoring/alerts
[ ] Set up regular backups
```

---

## 🔄 7. Secrets Rotation Procedure

**Rotate every 90 days or immediately if compromised**

### Backend Secrets Rotation

1. **Generate new secrets:**

   ```powershell
   # New SECRET_KEY
   openssl rand -hex 32

   # New JWT_SECRET_KEY
   openssl rand -hex 32

   # New CREDENTIAL_ENCRYPTION_KEY
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. **Update in Render:**
   - Dashboard → Environment → Update each key
   - Save changes (triggers redeploy)

3. **Update local .env:**
   - Update your `app/backend/.env`
   - Restart local server

4. **Verify:**
   - Test authentication still works
   - Check encrypted credentials still decrypt
   - Monitor logs for errors

### MongoDB Password Rotation

1. **Create new user in Atlas:**
   - Database Access → Add New User
   - Generate strong password

2. **Update connection string:**
   - Update in Render Environment
   - Update in local .env

3. **Test connections:**
   - Run `node test-mongo.js "<new_connection_string>"`
   - Verify backend can connect

4. **Remove old user:**
   - After verifying new user works
   - Database Access → Delete old user

### Platform API Keys Rotation

1. **Generate new keys in developer portals:**
   - eBay: developer.ebay.com
   - Facebook: developers.facebook.com

2. **Update in Render and local .env**

3. **Test integrations**

4. **Revoke old keys in portals**

---

## 🛠️ 8. Tools & Commands

### Generate Secrets

```powershell
# SECRET_KEY, JWT_SECRET_KEY
openssl rand -hex 32

# CREDENTIAL_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Random password
openssl rand -base64 32
```

### Test MongoDB Connection

```powershell
# Using test script
node test-mongo.js "your_connection_string"

# Using Python
python app/backend/check_mongodb.py
```

### Verify No Secrets in Git

```powershell
# Search for potential secrets
git log -p | grep -i "password\|secret\|key"

# Scan with TruffleHog (install first)
trufflehog git file://. --only-verified

# Check current files
git grep -i "password\|secret\|api_key"
```

### Deploy with Secrets

```powershell
# Backend (Render auto-deploys on push)
git push origin main

# Frontend (GitHub Actions)
git push origin main  # Triggers deploy workflow

# Manual frontend deploy
cd app/frontend
REACT_APP_API_URL=https://www.crosspostme.com/api yarn build
./scripts/upload-to-hostinger.ps1
```

---

## 📚 9. Reference Links

### Documentation

- [Backend Environment Vars](app/backend/ENVIRONMENT_VARS.md)
- [Credential Rotation Checklist](app/backend/CREDENTIAL_ROTATION_CHECKLIST.md)
- [Security Notice](app/backend/SECURITY_NOTICE.md)

### Developer Portals

- eBay Developers: https://developer.ebay.com/
- Facebook Developers: https://developers.facebook.com/
- MongoDB Atlas: https://cloud.mongodb.com/
- Render Dashboard: https://dashboard.render.com/

### Tools

- Render: https://render.com/docs
- GitHub Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- TruffleHog: https://github.com/trufflesecurity/trufflehog
- BFG Repo-Cleaner: https://rtyley.github.io/bfg-repo-cleaner/

---

## 💡 10. Quick Reference

### Most Common Commands

```powershell
# Setup local backend
cp app/backend/.env.example app/backend/.env
# Edit .env and add your secrets
cd app/backend && .\.venv\Scripts\Activate.ps1
uvicorn server:app --reload

# Setup local frontend
cp app/frontend/.env.example app/frontend/.env
# Edit .env: REACT_APP_API_URL=http://localhost:8000/api
cd app/frontend && yarn start

# Generate all keys at once
echo "SECRET_KEY=$(openssl rand -hex 32)" && \
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" && \
python -c "from cryptography.fernet import Fernet; print('CREDENTIAL_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Test everything works
curl http://localhost:8000/api/health
curl http://localhost:3000
```

---

**Last Updated:** 2025-10-27

**Questions?** Email: crosspostme@gmail.com | Phone: 623-777-9969
