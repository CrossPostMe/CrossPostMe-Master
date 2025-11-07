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

def get_secret(secret_name, default=None):
    """Convenience function to get a secret."""
    try:
        return get_vault().get_secret(secret_name)
    except (FileNotFoundError, RuntimeError):
        if default is not None:
            return default
        raise

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
        except (FileNotFoundError, RuntimeError):
            # Secret not set, use environment variable fallback
            env_name = name.upper()
            if env_name in os.environ:
                secrets[env_name] = os.environ[env_name]

    return secrets

def load_secrets_to_env():
    """Load all vault secrets into environment variables."""
    secrets = get_all_secrets()
    os.environ.update(secrets)

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
        print("💡 Run './setup-vault.sh' to initialize the vault")
        exit(1)