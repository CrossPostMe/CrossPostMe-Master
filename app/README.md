# CrossPostMe.com — Local listings automation (developer README)

![CI](https://github.com/dearthdiggler/app/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-auto-green)

This repository contains the production stack powering CrossPostMe.com: a FastAPI backend and a React frontend. All copy and assets are now production-ready.

## Onboarding & Quick Start
## Automated Monitoring & Docs

### Monitoring
- Sentry error tracking: Add your SENTRY_DSN to backend `.env`.
- UptimeRobot: Monitor `/api/ready` and `/api/health` endpoints.
- Prometheus/Grafana: Run with Docker Compose, metrics at `/metrics`, dashboards at `localhost:3001`.

### Documentation
- API docs: FastAPI `/docs` (Swagger UI).
- All secrets and environment variables documented in `.env.example` and this README.
- Deployment guides: See `MONITORING_AND_DOCS.md` for step-by-step instructions.

### Backend (FastAPI)

```powershell
# create venv, install, run dev server
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r .\app\backend\requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000 --app-dir .\app\backend
```bash

### Frontend (React / CRA + craco)

## Deployment Steps

### Local Docker Compose

```bash
docker-compose up --build
```bash

### Production Deploy (Render)

- Connect repo to Render.com, set env vars (`MONGO_URL`, `DB_NAME`, `SECRET_KEY`, `CORS_ORIGINS`).
- Render auto-deploys on push to `main`.

### Frontend Deploy (Hostinger)

Push to `main` triggers Hostinger deploy via GitHub Actions.

### Rollback / Blue-Green Deploy

- For backend: create a new Render service for blue-green, switch DNS when ready.
- For frontend: deploy to `playground` branch for staging, swap build to production path when ready.

## API Usage Examples

### Get Health Status

```bash
curl https://www.crosspostme.com/api/health
```

### Create Ad

```bash
curl -X POST https://www.crosspostme.com/api/ads -H "Content-Type: application/json" -d '{"title": "Test Ad", "price": 10.0, ...}'
```

### List Ads

```bash
curl https://www.crosspostme.com/api/ads
```

## Docs & Guides

- [Backend Environment Vars](app/backend/ENVIRONMENT_VARS.md)
- [Health Probes](app/backend/PROBES.md)
- [Credential Rotation](app/backend/CREDENTIAL_ROTATION_CHECKLIST.md)
- [Dependency Constraints](app/backend/DEPENDENCY_CONSTRAINTS_UPDATE.md)
- [Database Setup](app/backend/DATABASE_SETUP.md)
- [Migration & Backup Guide](app/backend/MIGRATION_BACKUP_GUIDE.md)
- [External Monitoring](app/backend/EXTERNAL_MONITORING.md)
- [Frontend Monitoring](app/frontend/EXTERNAL_MONITORING.md)

```powershell
cd .\app\frontend
yarn install
yarn start
```

## Security & Environment Setup

## Troubleshooting SSL/HTTPS Issues

## Troubleshooting Common Deployment & Runtime Errors

### MongoDB Connection Issues

If you see errors connecting to MongoDB (e.g., timeout, authentication failed, TLS handshake error):

1. **Check your connection string and credentials:**
   - Ensure `MONGO_CONNECTIONSTRING`, `MONGOATLAS_USER`, and `MONGOATLAS_PASS` are set correctly.
   - For Atlas, use the "Connect" dialog to copy the correct URI.

2. **Verify network and firewall settings:**
   - Make sure your deployment allows outbound connections to MongoDB Atlas or your cluster.
   - Whitelist your server IP in Atlas.

3. **TLS/SSL errors:**
   - See the SSL/HTTPS troubleshooting section above.
   - For local testing, only use `ALLOW_INVALID_CERTS_FOR_TESTING=true` in safe environments.

4. **Use `test-mongo.js` or backend health probes:**
   - Run `node test-mongo.js "<your_mongo_url>"` to test connectivity.
   - Check `/api/health` and `/api/ready` endpoints for backend status.

### Docker & CI/CD Issues

If your build or deploy fails in Docker or CI/CD:

1. **Check environment variables:**
   - Ensure all required secrets are set in your CI/CD provider and `.env` files.

2. **Review Docker logs and healthchecks:**
   - Use `docker-compose logs` and check for healthcheck failures.
   - Make sure your Dockerfiles expose the correct ports and health endpoints.

3. **CI/CD pipeline errors:**
   - Review GitHub Actions or other CI logs for missing secrets, failed steps, or permission errors.
   - Ensure your CI/CD config files (e.g., `.github/workflows/*.yml`) are up to date.

4. **Security audits:**
   - Periodically run TruffleHog, Gitleaks, `npm audit`, and `pip-audit` to check for secrets exposure and vulnerabilities.

For more help, see the docs folder and your CI/CD provider’s documentation.

If you encounter SSL/TLS errors (e.g., `ERR_SSL_VERSION_OR_CIPHER_MISMATCH`, certificate errors, or protocol issues), follow these steps:

1. **Verify certificate validity and chain:**
   - Ensure your certificate is not expired and is signed by a trusted CA.
   - Use SSL tools (e.g., [SSL Labs](https://www.ssllabs.com/ssltest/)) to check your domain.
   - Confirm intermediate certificates are correctly installed.

2. **Check supported TLS versions and ciphers:**
   - Make sure your server supports TLS 1.2 or higher.
   - Avoid deprecated ciphers (e.g., SSLv3, TLS 1.0/1.1).
   - For Render/Hostinger/Cloudflare, review their SSL/TLS settings and force modern protocols if needed.

3. **Render/Hostinger/Cloudflare config tips:**
   - On Render, use the "Custom Domains" and "SSL" dashboard to verify certificate status.
   - On Hostinger, check SSL settings and ensure your domain points to the correct service.
   - On Cloudflare, set SSL mode to "Full (Strict)" and enable TLS 1.2+.

4. **Use `tls_probe.py` for diagnostics:**
   - Run `tls_probe.py` to test SSL/TLS handshake and diagnose protocol/cipher issues.

     ```bash
     python app/backend/tls_probe.py your_mongo_cluster_url
     ```

   - Review output for handshake errors, unsupported protocols, or certificate problems.

5. **Common fixes:**
   - Regenerate and reinstall certificates if expired or misconfigured.
   - Update server and client libraries to support modern TLS.
   - Remove any test-only flags (e.g., `ALLOW_INVALID_CERTS_FOR_TESTING`) from production.

For more help, see `app/backend/tls_probe.py` and your hosting provider's SSL documentation.

## ⚠️ IMPORTANT SECURITY NOTICE ⚠️

This application handles sensitive credentials and API keys. Follow these security practices:

### Environment Configuration

1. **Copy the example environment file:**

```bash
cp app/backend/.env.example app/backend/.env
```

2. **Generate your own encryption key:**

```python
# Run this command to generate a secure encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

3. **Update your .env file with the generated key:**

```bash
CREDENTIAL_ENCRYPTION_KEY=<your_generated_key> # Already set in secrets manager or .env
```

### Platform API Keys

Get API credentials from each platform:

eBay and Facebook API credentials are already set in your secrets manager:

- EBAY_APP_ID
- EBAY_CERT_ID
- EBAY_DEV_ID
- FACEBOOK_APP_ID
- FACEBOOK_APP_SECRET

If you need to rotate or update these, visit:

- [eBay Developer Program](https://developer.ebay.com/)
- [Facebook for Developers](https://developers.facebook.com/)

### Production Security

**NEVER commit real credentials to version control!**


For production deployments, secrets are managed using:

**crossenv secrets:**

- HOSTINGER_SSH_HOST
- HOSTINGER_SSH_KEY
- HOSTINGER_SSH_PORT
- HOSTINGER_SSH_USER
- HOSTIP
- HOSTPORT
- HOSTPWD
- HOSTUSER
- MONGOATLAS_PASS
- MONGOATLAS_USER
- MONGODB_PRIVATEKEY
- MONGODB_PUBLICKEY
- MONGO_CONNECTIONSTRING
- MONGO_SHARDNAME
- OPENAI_API
- SSHKEY

**GitHub repository secrets:**

- CREDENTIAL_ENCRYPTION_KEY
- CROSSPOSTME_RENDERAPIKEY
- JWT_SECRET_KEY
- RENDER_API_KEY
- RENDER_DEPLOY_HOOK
- RENDER_SERVICE_ID
- RENDER_SERVICE_URL
- **AWS Secrets Manager** (recommended for AWS deployments)
- **HashiCorp Vault** (for on-premise or multi-cloud)
- **Azure Key Vault** (for Azure deployments)

Refer to your environment and repository settings for the full list of secrets in use.

### Git Security

If you accidentally commit secrets:

1. **Immediately rotate all exposed keys**
2. **Remove from git history using:**

   ```bash
   # Option 1: BFG Repo-Cleaner (recommended)
   git clone --mirror your-repo.git
   java -jar bfg.jar --delete-files .env your-repo.git

   # Option 2: git filter-repo
   git filter-repo --path backend/.env --invert-paths
   ```

3. **Force push the cleaned repository**
4. **Notify all team members to re-clone**

## Onboarding Guide

- Clone repo, copy `.env.example` to `.env` and fill in secrets
- Install dependencies and run dev servers (see above)
- Review API usage examples and docs
- For questions: <crosspostme@gmail.com> — Phone: 623-777-9969
