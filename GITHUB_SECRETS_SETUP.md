# GitHub Secrets Configuration

This document lists all the secrets that need to be configured in your GitHub repository settings for the CI/CD pipeline to work properly.
Ensure all URLs and instructions below are up-to-date and match your repository and service configurations.

## Required Secrets

Navigate to: **GitHub Repository → Settings → Secrets and variables → Actions → New repository secret**

### 1. SLACK_WEBHOOK_URL
**Purpose:** Send CI/CD notifications to Slack channel
**How to get it:**
1. Go to your Slack workspace (ensure you have permission to add integrations; admin access may be required)
2. Navigate to Apps → Manage → Custom Integrations → Incoming Webhooks
3. Add to Slack and select a channel
4. Copy the webhook URL (starts with <https://hooks.slack.com/services/>)

**How to add to GitHub:**
1. Go to: [GitHub Secrets Settings](https://github.com/dearthdiggler/CrossPostMe_MR/settings/secrets/actions)
2. Click "New repository secret"
3. Name: `SLACK_WEBHOOK_URL`
4. Value: Paste the webhook URL above
5. Click "Add secret"

---

### 2. TRUNK_API_KEY
**Purpose:** Run Trunk code quality checks in CI
**How to get it:**
1. Go to the Trunk website and log in with your account.
2. Navigate to Settings → API Keys.
3. Obtain your API key. **Never share or paste your API key in documentation or code. Only enter it directly into the GitHub Secrets form.**

**How to add to GitHub:**
1. In your repository, go to Settings → Secrets and variables → Actions.
2. Click "New repository secret".
3. Name: `TRUNK_API_KEY`
4. Value: Enter your API key securely (do not expose it in documentation or code).
5. Click "Add secret".

---

### 3. SENTRY_DSN
**Purpose:** Error tracking and monitoring in production
**How to get it:**
SENTRY_DSN:   https://10a4cb3be5e4ebf98cc64df09bcbe688@o4510305135755264.ingest.us.sentry.io/4510305140539392
1. Go to [Sentry](<https://sentry.io/>)
2. Navigate to Settings → Projects → [Your Project]
3. Go to Client Keys (DSN)
4. Copy the DSN URL (e.g. <https://examplePublicKey@o0.ingest.sentry.io/0>)

**How to add to GitHub:**
1. Go to: <https://github.com/dearthdiggler/CrossPostMe_MR/settings/secrets/actions>
2. Click "New repository secret"
3. Name: `SENTRY_DSN`
4. Value: Paste the DSN above
5. Click "Add secret"

**Note:** This is optional but recommended for production error monitoring.

---

## Optional Secrets (for deployment workflows)

### 4. RENDER_API_KEY
**Purpose:** Trigger backend deployments to Render
**How to get it:**
- RENDER_ID:   srv-d3r0mnd6ubrc738aj5og
- RENDER_SERVICE_NAME:   crosspostme-backend
- RENDER_ENVIRONMENT:   production
- RENDER_API_KEY:   rnd_s1eQUbk7LLTjyF8uRC4Wzh6k4D4X


1.Login to [Render](https://render.com)
2. Go to Account Settings → API Keys
3. Create new API key

---

### 5. HOSTINGER_* Secrets
**Purpose:** Deploy frontend to Hostinger
**Secrets needed:**
- HOSTINGER_SSH_IP:   82.180.138.1
- HOSTINGER_SSH_PORT:  65002
- HOSTINGER_SSH_USERNAME:   u132063632
- HOSTINGER_SSH_PWD:   P@ndaGod99$

**How to get them:**
1. Login to [Hostinger control panel](https://www.hostinger.com/)
2. Go to FTP Accounts
3. Create or use existing FTP credentials

---

## How to Add Secrets to GitHub

1. Go to your repository: https://github.com/dearthdiggler/CrossPostMe_MR
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** button
5. Enter the secret name (exactly as listed above)
6. Paste the secret value
7. Click **Add secret**

---

## Verification

After adding secrets, push a commit to the `master` branch and check:
1. Go to **Actions** tab in GitHub
2. Find your workflow run
3. Check that all jobs complete successfully
4. Verify Slack notifications are received (if configured)

---

## Current CI/CD Pipeline

The consolidated CI/CD pipeline (`ci.yml`) includes:

### Jobs:
1. **Backend CI** - Python type checking, tests, brand checker
2. **Frontend CI** - Node.js unit tests, Playwright E2E tests
3. **Code Quality** - Trunk checks (on pull requests only)
4. **Notify Success** - Slack notification when all jobs pass

### Triggers:
- Push to `main` or `master` branch
- Pull requests to `main` or `master` branch

---

## Notes

- Slack notifications only trigger on **push** events (not pull requests)
- Trunk checks only run on **pull requests** to save API quota
- The old `checks.yml` workflow has been disabled (renamed to `checks.yml.disabled`)
- All workflows now support both `main` and `master` branches


CANVAS_PWD:   sc6LeKbL*XsMYkq

EBAY_APP_ID:   JohnDomi-CrossPos-SBX-3c58638cb-41a05df0
EBAY_CERT_ID:   SBX-c58638cbbcab-ec00-4343-b4b9-5965p-id-optional
EBAY_DEV_ID:   5aae0611-9487-4f97-8e70-374716ca6e6a

MONITORING_PASSWORD:   P@ndaGod99$
SECRET_KEY:   2e6660042f3aaf822e9169961f7757de921231fffa4fe80d75328fe16aa428f0c

REDIS_URL:   redis://default:AUspAAIncDIxZDkzYjJhNDNiOGE0NTAzYTU5ZGJmMzRhNjU4ZTg2NXAyMTkyNDE@crack-blowfish-19241.upstash.io:6379

UPSTASH_REDIS_REST_TOKEN:   AUspAAIncDIxZDkzYjJhNDNiOGE0NTAzYTU5ZGJmMzRhNjU4ZTg2NXAyMTkyNDE
UPSTASH_REDIS_REST_URL:   https://crack-blowfish-19241.upstash.io

MONGO_SHARD:   ac-8hiqmwq-shard-00-02.fkup1pl.mongodb.net:27017
MONGOATLAS_CLIENTID:   mdb_sa_id_68f5e5c440efc26472c2bc77
MONGOATLAS_PUBLICKEY:   kxzyswbq
MONGOATLAS_PRIVATEKEY:   6065533c-8961-49ee-8a61-0d59779f9807
MONGO_URL:   mongodb+srv://crosspostme:P%40ndaKing13%24@cluster0.fkup1pl.mongodb.net/crosspostme?retryWrites=true&w=majority&appName=Cluster0

CREDENTIAL_ENCRYPTION_KEY:   a4c1e47ff0d6a80bfb278d749dda93718548763ad5b3d5b0d730ecc7a4257d82

JWT_SECRET_KEY:   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJpYXQiOjE3NjA5NjM4OTN9._h6Lmu230sPEiBhztzeR3lWTdjaqDJlgIjCROpcxPGc

SLACK_WEBHOOK_URL:   https://hooks.slack.com/services/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

OPENAI_API_KEY:   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

SENTRY_CROSSPOSTME: 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
TRUNK_API_KEY:   Jh4YpbSvdG2bnTM55tZFeKGxqQvbdKwnJw7nTQG

