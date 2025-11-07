#!/bin/bash
# 🔐 SECRETS VAULT SETUP SCRIPT
# Initialize and populate the secrets vault for CrossPostMe

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Vault configuration
VAULT_DIR="./secrets_vault"
VAULT_FILE="$VAULT_DIR/secrets.enc"
VAULT_KEY_FILE="$VAULT_DIR/master.key"

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Generate encryption key
generate_master_key() {
    print_status "Generating master encryption key..."

    if [[ ! -f "$VAULT_KEY_FILE" ]]; then
        openssl rand -hex 32 > "$VAULT_KEY_FILE"
        chmod 600 "$VAULT_KEY_FILE"
        print_success "Master key generated: $VAULT_KEY_FILE"
    else
        print_warning "Master key already exists"
    fi
}

# Create vault directory
create_vault_directory() {
    print_status "Creating secrets vault directory..."

    if [[ ! -d "$VAULT_DIR" ]]; then
        mkdir -p "$VAULT_DIR"
        chmod 700 "$VAULT_DIR"
        print_success "Vault directory created: $VAULT_DIR"
    else
        print_warning "Vault directory already exists"
    fi
}

# Encrypt a secret
encrypt_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [[ -z "$secret_value" ]]; then
        print_warning "Skipping $secret_name (empty value)"
        return
    fi

    echo -n "$secret_value" | openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:"$VAULT_KEY_FILE" -out "$VAULT_DIR/$secret_name.enc"
    print_success "Encrypted: $secret_name"
}

# Decrypt a secret
decrypt_secret() {
    local secret_name="$1"

    if [[ ! -f "$VAULT_DIR/$secret_name.enc" ]]; then
        print_error "Secret $secret_name not found in vault"
        return 1
    fi

    openssl enc -d -aes-256-cbc -pbkdf2 -pass file:"$VAULT_KEY_FILE" -in "$VAULT_DIR/$secret_name.enc" 2>/dev/null
}

# Initialize vault with secrets
initialize_vault() {
    print_status "Initializing secrets vault..."

    # Prompt for secrets
    echo
    echo "🔐 SECRETS VAULT INITIALIZATION"
    echo "================================"
    echo
    print_warning "You will be prompted to enter each secret. Press Enter to skip any secret."
    echo

    # Supabase secrets
    read -p "Enter SUPABASE_URL: " SUPABASE_URL
    read -p "Enter SUPABASE_ANON_KEY: " SUPABASE_ANON_KEY
    read -p "Enter SUPABASE_SERVICE_ROLE_KEY: " SUPABASE_SERVICE_ROLE_KEY

    # JWT secrets
    read -p "Enter SECRET_KEY (for JWT): " SECRET_KEY

    # Stripe secrets
    read -p "Enter STRIPE_SECRET_KEY: " STRIPE_SECRET_KEY
    read -p "Enter STRIPE_PUBLISHABLE_KEY: " STRIPE_PUBLISHABLE_KEY
    read -p "Enter STRIPE_WEBHOOK_SECRET: " STRIPE_WEBHOOK_SECRET

    # Database secrets
    read -p "Enter MONGODB_URL: " MONGODB_URL

    # Email secrets
    read -p "Enter SMTP_USERNAME: " SMTP_USERNAME
    read -p "Enter SMTP_PASSWORD: " SMTP_PASSWORD

    # AI secrets
    read -p "Enter OPENAI_API_KEY: " OPENAI_API_KEY

    echo
    print_status "Encrypting secrets..."

    # Encrypt all secrets
    encrypt_secret "supabase_url" "$SUPABASE_URL"
    encrypt_secret "supabase_anon_key" "$SUPABASE_ANON_KEY"
    encrypt_secret "supabase_service_role_key" "$SUPABASE_SERVICE_ROLE_KEY"
    encrypt_secret "secret_key" "$SECRET_KEY"
    encrypt_secret "stripe_secret_key" "$STRIPE_SECRET_KEY"
    encrypt_secret "stripe_publishable_key" "$STRIPE_PUBLISHABLE_KEY"
    encrypt_secret "stripe_webhook_secret" "$STRIPE_WEBHOOK_SECRET"
    encrypt_secret "mongodb_url" "$MONGODB_URL"
    encrypt_secret "smtp_username" "$SMTP_USERNAME"
    encrypt_secret "smtp_password" "$SMTP_PASSWORD"
    encrypt_secret "openai_api_key" "$OPENAI_API_KEY"

    print_success "All secrets encrypted and stored in vault"
}

# Test vault functionality
test_vault() {
    print_status "Testing vault functionality..."

    # Test decryption
    if SUPABASE_URL_TEST=$(decrypt_secret "supabase_url"); then
        print_success "Vault decryption working"
    else
        print_error "Vault decryption failed"
        exit 1
    fi
}

# Create vault access library
create_vault_library() {
    print_status "Creating vault access library..."

    cat > vault.py << 'EOF'
#!/usr/bin/env python3
"""
🔐 SECRETS VAULT ACCESS LIBRARY

Securely access encrypted secrets from the vault.
Usage:
    from vault import get_secret
    api_key = get_secret('openai_api_key')
"""

import os
import subprocess
from pathlib import Path

class SecretsVault:
    def __init__(self, vault_dir="./secrets_vault"):
        self.vault_dir = Path(vault_dir)
        self.key_file = self.vault_dir / "master.key"

        if not self.key_file.exists():
            raise FileNotFoundError(f"Master key not found: {self.key_file}")

    def get_secret(self, secret_name):
        """Retrieve a secret from the vault."""
        secret_file = self.vault_dir / f"{secret_name}.enc"

        if not secret_file.exists():
            raise FileNotFoundError(f"Secret '{secret_name}' not found in vault")

        try:
            # Use openssl to decrypt
            result = subprocess.run([
                'openssl', 'enc', '-d', '-aes-256-cbc', '-pbkdf2',
                '-pass', f'file:{self.key_file}',
                '-in', str(secret_file)
            ], capture_output=True, text=True, check=True)

            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to decrypt secret '{secret_name}': {e}")

# Global vault instance
_vault = None

def get_vault():
    """Get the global vault instance."""
    global _vault
    if _vault is None:
        _vault = SecretsVault()
    return _vault

def get_secret(secret_name):
    """Convenience function to get a secret."""
    return get_vault().get_secret(secret_name)

def get_all_secrets():
    """Get all secrets as environment variables dict."""
    vault = get_vault()
    secrets = {}

    # List of all possible secrets
    secret_names = [
        'supabase_url', 'supabase_anon_key', 'supabase_service_role_key',
        'secret_key', 'stripe_secret_key', 'stripe_publishable_key',
        'stripe_webhook_secret', 'mongodb_url', 'smtp_username',
        'smtp_password', 'openai_api_key'
    ]

    for name in secret_names:
        try:
            secrets[name.upper()] = vault.get_secret(name)
        except FileNotFoundError:
            # Secret not set, skip
            continue

    return secrets

if __name__ == "__main__":
    # Test the vault
    try:
        vault = get_vault()
        print("🔐 Secrets vault is accessible")

        # Show available secrets (without revealing values)
        vault_path = Path("./secrets_vault")
        if vault_path.exists():
            secrets = list(vault_path.glob("*.enc"))
            print(f"📁 Found {len(secrets)} encrypted secrets:")
            for secret in secrets:
                print(f"  - {secret.stem}")

    except Exception as e:
        print(f"❌ Vault error: {e}")
        exit(1)
EOF

    chmod 600 vault.py
    print_success "Vault access library created: vault.py"
}

# Create .gitignore for vault
create_gitignore() {
    print_status "Creating .gitignore for secrets vault..."

    if [[ ! -f ".gitignore" ]]; then
        touch .gitignore
    fi

    # Add vault files to .gitignore if not already present
    if ! grep -q "secrets_vault/" .gitignore; then
        echo "# Secrets Vault - DO NOT COMMIT" >> .gitignore
        echo "secrets_vault/" >> .gitignore
        echo "vault.py" >> .gitignore
        print_success ".gitignore updated"
    else
        print_warning ".gitignore already contains vault entries"
    fi
}

# Main setup function
main() {
    echo "🔐 SETTING UP SECRETS VAULT"
    echo "==========================="

    create_vault_directory
    generate_master_key
    initialize_vault
    test_vault
    create_vault_library
    create_gitignore

    echo
    print_success "🎉 SECRETS VAULT SETUP COMPLETE!"
    echo
    print_status "Next steps:"
    echo "1. Backup your master key: $VAULT_KEY_FILE"
    echo "2. Test vault access: python3 vault.py"
    echo "3. Update your application to use: from vault import get_secret"
    echo
    print_warning "⚠️  IMPORTANT SECURITY NOTES:"
    echo "  - Never commit the secrets_vault/ directory"
    echo "  - Backup the master.key file securely"
    echo "  - The master.key file unlocks all secrets"
    echo "  - Use environment-specific vaults for production"
}

# Run main function
main "$@"
EOF