## Environment variables for Render deployment and local testing

This file consolidates the environment variables used by the backend and explains where each one should be set (Render production vs local/test). Use this as a single copy/paste source.

WARNING: Never commit real secrets to git. Keep any `.env` files out of version control and use Render's Environment settings for production.

---

## Production (Render) — key / value pairs

Set these in the Render Dashboard → Your Service → Environment (add each as a separate variable):

- MONGO_URL
  - Description: MongoDB Atlas connection string (includes username and password)
  - Example: mongodb+srv://your_mongo_user:your_mongo_password@your_cluster_host/?retryWrites=true&w=majority
  - Where to set: Render UI (Environment)
  - Secret: Yes (contains DB credentials)

- DB_NAME
  - Description: Logical database name used by the app
  - Production value (example from checklist): crosspostme_prod
  - Where to set: Render UI (Environment)
  - Secret: No

- ENV
  - Description: Deployment environment flag. Controls production vs dev behavior
  - Value (production): production
  - Where to set: Render UI (Environment)
  - Secret: No

- SECRET_KEY
  - Description: App secret for signing sessions or internal secrets
  - Example (generated): d38383a04b144877b3b1562f0b04690eff1960eb3ae33fd1daa24bfd640ea9d5
  - Where to set: Render UI (Environment)
  - Secret: Yes

- JWT_SECRET_KEY
  - Description: Key used to sign JWT tokens
  - Example (generated): 39f2c9fa23bee53833fb16229250796f38441a0075508b59f9de5febbc3a50a2
  - Where to set: Render UI (Environment)
  - Secret: Yes

Optional / recommended (set in Render if desired):

- MONGO_SERVER_SELECTION_TIMEOUT_MS=20000
- ACCESS_TOKEN_EXPIRE_MINUTES=30
- REFRESH_TOKEN_EXPIRE_DAYS=7

Do NOT set in production unless you understand the risk (for temporary testing only):

- MONGO_TLS_ALLOW_INVALID_CERTS=true
- ALLOW_INVALID_CERTS_FOR_TESTING=true
- MONGO_TLS_OVERRIDE=true

---

## Local / Development — `.env` or temporary session variables

Your repository currently uses `crosspostme` in `app/backend/.env` for local development. Use that DB name for local testing. Example `.env` content (for development only):

```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=crosspostme
ENV=development
SECRET_KEY=d38383a04b144877b3b1562f0b04690eff1960eb3ae33fd1daa24bfd640ea9d5
JWT_SECRET_KEY=39f2c9fa23bee53833fb16229250796f38441a0075508b59f9de5febbc3a50a2
MONGO_SERVER_SELECTION_TIMEOUT_MS=15000
```

Or set them in PowerShell/Bash for a single session (examples):

PowerShell:
```powershell
$env:MONGO_URL = "mongodb://localhost:27017"
$env:DB_NAME = "crosspostme"
$env:ENV = "development"
$env:SECRET_KEY = "d38383a04b144877b3b1562f0b04690eff1960eb3ae33fd1daa24bfd640ea9d5"
$env:JWT_SECRET_KEY = "39f2c9fa23bee53833fb16229250796f38441a0075508b59f9de5febbc3a50a2"
$env:MONGO_SERVER_SELECTION_TIMEOUT_MS = "15000"
```

Bash:
```bash
export MONGO_URL="mongodb://localhost:27017"
export DB_NAME="crosspostme"
export ENV="development"
export SECRET_KEY="d38383a04b144877b3b1562f0b04690eff1960eb3ae33fd1daa24bfd640ea9d5"
export JWT_SECRET_KEY="39f2c9fa23bee53833fb16229250796f38441a0075508b59f9de5febbc3a50a2"
export MONGO_SERVER_SELECTION_TIMEOUT_MS="15000"
```

Notes:
- Use `ENV=development` or `local` for developer machines. `ENV=production` should be used in Render.
- If you need to allow invalid certs for local testing with self-signed servers, only set `MONGO_TLS_ALLOW_INVALID_CERTS=true` and `ALLOW_INVALID_CERTS_FOR_TESTING=true` while `ENV` is a safe environment (development/dev/local/test). Remove them afterward.

---

## Quick paste formats

Render UI (each as a separate env var)

MONGO_URL=mongodb+srv://your_mongo_user:your_mongo_password@your_cluster_host/?retryWrites=true&w=majority
DB_NAME=crosspostme_prod
ENV=production
SECRET_KEY=d38383a04b144877b3b1562f0b04690eff1960eb3ae33fd1daa24bfd640ea9d5
JWT_SECRET_KEY=39f2c9fa23bee53833fb16229250796f38441a0075508b59f9de5febbc3a50a2
MONGO_SERVER_SELECTION_TIMEOUT_MS=20000
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

Local `.env` (do not commit):

MONGO_URL=mongodb+srv://your_mongo_user:your_mongo_password@your_cluster_host/?retryWrites=true&w=majority
DB_NAME=crosspostme
ENV=development
# Generate a 32-byte hex secret for local testing (do not commit):
# openssl rand -hex 32
SECRET_KEY=your_secret_key_here_generate_with_openssl_rand
# Generate a JWT signing secret (do not commit):
# openssl rand -hex 32
JWT_SECRET_KEY=your_jwt_secret_key_here_generate_with_openssl_rand

---

## What I changed / why

- Consolidated all environment variables and guidance into one file so you can copy/paste safely.
- Marked which variables are production vs local/test and warned about unsafe test-only flags.

---

## Test-only environment file (.env.testing)

This repository includes a test-only environment file at `app/backend/.env.testing` for local or CI test runs. It contains flags that allow relaxed TLS or other unsafe behaviors intended only for automated tests and local debugging.

Important:

- Do NOT include `.env.testing` in production images, deployments, or commits that contain secrets.
- The file is ignored by git in `app/.gitignore` and by Docker via the project `.dockerignore` to prevent it from being copied into build contexts.

How to load it for tests:

PowerShell (single session):
```powershell
if (Test-Path -Path 'app/backend/.env.testing') {
  Get-Content 'app/backend/.env.testing' | ForEach-Object { $name, $value = ($_ -split "=", 2); if ($name) { $env:$name = $value } }
  # then run your test command, e.g. `pytest`
} else {
  Write-Host "No .env.testing file found; skipping loading test env vars"
}
```

Or with dotenv in Python tests:
```python
from dotenv import load_dotenv
from pathlib import Path
env_path = Path('app/backend/.env.testing')
if env_path.exists():
  load_dotenv(dotenv_path=str(env_path))
  # run test setup that depends on these env vars
else:
  print('No .env.testing found; skipping test-only env load')
```

Or set CI job steps to explicitly load the file only during test jobs. If you need help wiring your CI to load `.env.testing` safely, I can add example snippets for GitHub Actions / Render / Railway.

The following enhancements are available:
- Replace placeholder examples across the docs with clearer, non-ambiguous instructions (I can run a scan and either auto-replace or present a list for approval).
- Create a `.env.example` file with masked placeholders that is safe to commit.
