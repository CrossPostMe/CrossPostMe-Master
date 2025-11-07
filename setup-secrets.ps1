#!/usr/bin/env pwsh
# setup-secrets.ps1 - Interactive script to set up environment variables for CrossPostMe

Write-Host "🔐 CrossPostMe Secrets Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env files already exist
$backendEnvExists = Test-Path "app/backend/.env"
$frontendEnvExists = Test-Path "app/frontend/.env"

if ($backendEnvExists -or $frontendEnvExists) {
    Write-Host "⚠️  WARNING: .env files already exist!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite them? (yes/no)"
    if ($overwrite -ne "yes") {
        Write-Host "❌ Setup cancelled. Existing .env files preserved." -ForegroundColor Red
        exit 0
    }
}

Write-Host "📝 Generating secure keys..." -ForegroundColor Green

# Generate SECRET_KEY
$secretKey = & openssl rand -hex 32
if (-not $secretKey) {
    Write-Host "❌ Error: openssl not found. Please install OpenSSL." -ForegroundColor Red
    exit 1
}

# Generate JWT_SECRET_KEY
$jwtSecretKey = & openssl rand -hex 32

# Generate CREDENTIAL_ENCRYPTION_KEY
$credentialKey = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
if (-not $credentialKey) {
    Write-Host "❌ Error: Python or cryptography package not found." -ForegroundColor Red
    Write-Host "Run: pip install cryptography" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Keys generated successfully!" -ForegroundColor Green
Write-Host ""

# Ask for MongoDB URL
Write-Host "📦 MongoDB Configuration" -ForegroundColor Cyan
Write-Host "Enter your MongoDB URL (press Enter for local default):" -ForegroundColor White
$mongoUrl = Read-Host "MongoDB URL"
if (-not $mongoUrl) {
    $mongoUrl = "mongodb://localhost:27017"
}

# Ask for database name
$dbName = Read-Host "Database name (press Enter for 'crosspostme')"
if (-not $dbName) {
    $dbName = "crosspostme"
}

# Ask for CORS origins
Write-Host ""
Write-Host "🌐 CORS Configuration" -ForegroundColor Cyan
Write-Host "Enter allowed origins (comma-separated, press Enter for default):" -ForegroundColor White
$corsOrigins = Read-Host "CORS Origins"
if (-not $corsOrigins) {
    $corsOrigins = "http://localhost:3000,http://localhost:8000"
}

# Ask if they want to add platform API keys now
Write-Host ""
Write-Host "🔌 Platform API Keys (Optional)" -ForegroundColor Cyan
$addKeys = Read-Host "Do you want to add eBay and Facebook API keys now? (yes/no)"

$ebayAppId = "your_ebay_app_id_here"
$ebayDevId = "your_ebay_dev_id_here"
$ebayCertId = "your_ebay_cert_id_here"
$facebookAppId = "your_facebook_app_id_here"
$facebookAppSecret = "your_facebook_app_secret_here"

if ($addKeys -eq "yes") {
    Write-Host ""
    Write-Host "eBay Developer Keys (from https://developer.ebay.com/):" -ForegroundColor Yellow
    $ebayAppId = Read-Host "eBay App ID"
    $ebayDevId = Read-Host "eBay Dev ID"
    $ebayCertId = Read-Host "eBay Cert ID"

    Write-Host ""
    Write-Host "Facebook Developer Keys (from https://developers.facebook.com/):" -ForegroundColor Yellow
    $facebookAppId = Read-Host "Facebook App ID"
    $facebookAppSecret = Read-Host "Facebook App Secret"
}

# Create backend .env file
Write-Host ""
Write-Host "📝 Creating app/backend/.env..." -ForegroundColor Green

$backendEnv = @"
# Backend Environment Variables - NEVER COMMIT THIS FILE
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# ============================================
# SECURITY (Auto-generated)
# ============================================
SECRET_KEY=$secretKey
JWT_SECRET_KEY=$jwtSecretKey
CREDENTIAL_ENCRYPTION_KEY=$credentialKey
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# DATABASE
# ============================================
MONGO_URL=$mongoUrl
DB_NAME=$dbName
MONGO_SERVER_SELECTION_TIMEOUT_MS=15000

# ============================================
# CORS
# ============================================
CORS_ORIGINS=$corsOrigins

# ============================================
# PLATFORM API KEYS
# ============================================
EBAY_APP_ID=$ebayAppId
EBAY_DEV_ID=$ebayDevId
EBAY_CERT_ID=$ebayCertId

FACEBOOK_APP_ID=$facebookAppId
FACEBOOK_APP_SECRET=$facebookAppSecret
FACEBOOK_DOWNLOAD_TIMEOUT=120
FACEBOOK_UPLOAD_TIMEOUT=120

# ============================================
# ENVIRONMENT
# ============================================
ENVIRONMENT=development
DEBUG=true
"@

$backendEnv | Out-File -FilePath "app/backend/.env" -Encoding UTF8

# Create frontend .env file
Write-Host "📝 Creating app/frontend/.env..." -ForegroundColor Green

$frontendEnv = @"
# Frontend Environment Variables - NEVER COMMIT THIS FILE
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# ============================================
# API Configuration
# ============================================
REACT_APP_API_URL=http://localhost:8000/api

# ============================================
# ENVIRONMENT
# ============================================
REACT_APP_ENV=development

# ============================================
# OPTIONAL FEATURES
# ============================================
REACT_APP_ENABLE_AUTH=true
REACT_APP_ENABLE_FACEBOOK=true
REACT_APP_ENABLE_EBAY=true
"@

$frontendEnv | Out-File -FilePath "app/frontend/.env" -Encoding UTF8

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Review the generated .env files and update any placeholder values" -ForegroundColor White
Write-Host "2. For eBay/Facebook keys, visit the developer portals:" -ForegroundColor White
Write-Host "   - eBay: https://developer.ebay.com/" -ForegroundColor Gray
Write-Host "   - Facebook: https://developers.facebook.com/" -ForegroundColor Gray
Write-Host "3. Start the backend: cd app/backend && .\.venv\Scripts\Activate.ps1 && uvicorn server:app --reload" -ForegroundColor White
Write-Host "4. Start the frontend: cd app/frontend && yarn start" -ForegroundColor White
Write-Host ""
Write-Host "📖 For more information, see SECRETS_MANAGEMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

# Show a summary of generated keys
Write-Host "🔑 Generated Keys Summary:" -ForegroundColor Yellow
Write-Host "SECRET_KEY: $($secretKey.Substring(0, 10))..." -ForegroundColor Gray
Write-Host "JWT_SECRET_KEY: $($jwtSecretKey.Substring(0, 10))..." -ForegroundColor Gray
Write-Host "CREDENTIAL_ENCRYPTION_KEY: $($credentialKey.Substring(0, 15))..." -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  IMPORTANT: These keys are stored in .env files which are git-ignored." -ForegroundColor Yellow
Write-Host "⚠️  Keep them safe and never commit them to version control!" -ForegroundColor Yellow
