# 🔧 Environment Variables Reference

Complete reference for all environment variables used in CrossPostMe.

---

## 📋 Quick Index

- [Backend Variables](#backend-variables) - Python/FastAPI server configuration
- [Frontend Variables](#frontend-variables) - React application configuration
- [Platform-Specific](#platform-specific-variables) - Deployment platform settings
- [Security Best Practices](#security-best-practices)

---

## Backend Variables

### 🔐 Security Keys (REQUIRED)

| Variable                    | Type   | Default  | Description                                          | How to Generate                                                                             |
| --------------------------- | ------ | -------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `SECRET_KEY`                | String | _(none)_ | Main application secret for cryptographic operations | `openssl rand -hex 32`                                                                      |
| `JWT_SECRET_KEY`            | String | _(none)_ | Secret for signing JSON Web Tokens                   | `openssl rand -hex 32`                                                                      |
| `CREDENTIAL_ENCRYPTION_KEY` | String | _(none)_ | Fernet key for encrypting stored credentials         | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

**⚠️ Critical:** Generate unique keys for each environment. NEVER reuse dev keys in production!

---

### 🗄️ Database Configuration (REQUIRED)

| Variable                            | Type    | Default                     | Description                             |
| ----------------------------------- | ------- | --------------------------- | --------------------------------------- |
| `MONGO_URL`                         | String  | `mongodb://localhost:27017` | MongoDB connection string               |
| `DB_NAME`                           | String  | `crosspostme`               | Database name to use                    |
| `MONGO_SERVER_SELECTION_TIMEOUT_MS` | Integer | `15000`                     | Server selection timeout (milliseconds) |

**Connection String Examples:**
