#!/bin/bash
# setup-secrets.sh - Interactive script to set up environment variables for CrossPostMe

set -e

echo "🔐 CrossPostMe Secrets Setup"
echo "================================"
echo ""

# Check if .env files already exist
if [ -f "app/backend/.env" ] || [ -f "app/frontend/.env" ]; then
	echo "⚠️  WARNING: .env files already exist!"
	read -p "Do you want to overwrite them? (yes/no): " overwrite
	if [ "$overwrite" != "yes" ]; then
		echo "❌ Setup cancelled. Existing .env files preserved."
		exit 0
	fi
fi

echo "📝 Generating secure keys..."

# Check for required tools
if ! command -v openssl &>/dev/null; then
	echo "❌ Error: openssl not found. Please install OpenSSL."
	exit 1
fi

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
	echo "❌ Error: Python not found. Please install Python."
	exit 1
fi

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# Generate JWT_SECRET_KEY
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Generate CREDENTIAL_ENCRYPTION_KEY
if command -v python3 &>/dev/null; then
	PYTHON_CMD=python3
else
	PYTHON_CMD=python
fi

CREDENTIAL_KEY=$($PYTHON_CMD -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null)
if [ -z "$CREDENTIAL_KEY" ]; then
	echo "❌ Error: cryptography package not found."
	echo "Run: pip install cryptography"
	exit 1
fi

echo "✅ Keys generated successfully!"
echo ""

# Ask for MongoDB URL
echo "📦 MongoDB Configuration"
read -p "Enter your MongoDB URL (press Enter for local default): " MONGO_URL
MONGO_URL=${MONGO_URL:-mongodb://localhost:27017}

# Ask for database name
read -p "Database name (press Enter for 'crosspostme'): " DB_NAME
DB_NAME=${DB_NAME:-crosspostme}

# Ask for CORS origins
echo ""
echo "🌐 CORS Configuration"
read -p "Enter allowed origins (comma-separated, press Enter for default): " CORS_ORIGINS
CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000,http://localhost:8000}

# Ask if they want to add platform API keys now
echo ""
echo "🔌 Platform API Keys (Optional)"
read -p "Do you want to add eBay and Facebook API keys now? (yes/no): " ADD_KEYS

EBAY_APP_ID="your_ebay_app_id_here"
EBAY_DEV_ID="your_ebay_dev_id_here"
EBAY_CERT_ID="your_ebay_cert_id_here"
FACEBOOK_APP_ID="your_facebook_app_id_here"
FACEBOOK_APP_SECRET="your_facebook_app_secret_here"

if [ "$ADD_KEYS" = "yes" ]; then
	echo ""
	echo "eBay Developer Keys (from https://developer.ebay.com/):"
	read -p "eBay App ID: " EBAY_APP_ID
	read -p "eBay Dev ID: " EBAY_DEV_ID
	read -p "eBay Cert ID: " EBAY_CERT_ID

	echo ""
	echo "Facebook Developer Keys (from https://developers.facebook.com/):"
	read -p "Facebook App ID: " FACEBOOK_APP_ID
	read -p "Facebook App Secret: " FACEBOOK_APP_SECRET
fi

# Create backend .env file
echo ""
echo "📝 Creating app/backend/.env..."

cat >app/backend/.env <<EOF
# Backend Environment Variables - NEVER COMMIT THIS FILE
# Generated on $(date +"%Y-%m-%d %H:%M:%S")

# ============================================
# SECURITY (Auto-generated)
# ============================================
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
CREDENTIAL_ENCRYPTION_KEY=$CREDENTIAL_KEY
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# DATABASE
# ============================================
MONGO_URL=$MONGO_URL
DB_NAME=$DB_NAME
MONGO_SERVER_SELECTION_TIMEOUT_MS=15000

# ============================================
# CORS
# ============================================
CORS_ORIGINS=$CORS_ORIGINS

# ============================================
# PLATFORM API KEYS
# ============================================
EBAY_APP_ID=$EBAY_APP_ID
EBAY_DEV_ID=$EBAY_DEV_ID
EBAY_CERT_ID=$EBAY_CERT_ID

FACEBOOK_APP_ID=$FACEBOOK_APP_ID
FACEBOOK_APP_SECRET=$FACEBOOK_APP_SECRET
FACEBOOK_DOWNLOAD_TIMEOUT=120
FACEBOOK_UPLOAD_TIMEOUT=120

# ============================================
# ENVIRONMENT
# ============================================
ENVIRONMENT=development
DEBUG=true
EOF

# Create frontend .env file
echo "📝 Creating app/frontend/.env..."

cat >app/frontend/.env <<EOF
# Frontend Environment Variables - NEVER COMMIT THIS FILE
# Generated on $(date +"%Y-%m-%d %H:%M:%S")

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
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the generated .env files and update any placeholder values"
echo "2. For eBay/Facebook keys, visit the developer portals:"
echo "   - eBay: https://developer.ebay.com/"
echo "   - Facebook: https://developers.facebook.com/"
echo "3. Start the backend: cd app/backend && source .venv/bin/activate && uvicorn server:app --reload"
echo "4. Start the frontend: cd app/frontend && yarn start"
echo ""
echo "📖 For more information, see SECRETS_MANAGEMENT_GUIDE.md"
echo ""

# Show a summary of generated keys
echo "🔑 Generated Keys Summary:"
echo "SECRET_KEY: ${SECRET_KEY:0:10}..."
echo "JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:10}..."
echo "CREDENTIAL_ENCRYPTION_KEY: ${CREDENTIAL_KEY:0:15}..."
echo ""
echo "⚠️  IMPORTANT: These keys are stored in .env files which are git-ignored."
echo "⚠️  Keep them safe and never commit them to version control!"
