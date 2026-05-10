import hvac
import os
from typing import Dict, Optional

class SecretsProvider:
    def __init__(self, vault_addr: str, vault_token: Optional[str] = None):
        # In production, we might use AppRole or Kubernetes auth
        # For now, we use the provided token or fall back to VAULT_TOKEN env var
        token = vault_token or os.getenv("VAULT_TOKEN")
        self.client = hvac.Client(url=vault_addr, token=token)

    def get_mailbox_credentials(self) -> Dict[str, str]:
        """
        Fetches Microsoft Graph API credentials from Vault.
        Path: secret/data/prescription-capture/mailbox
        """
        try:
            read_response = self.client.secrets.kv.v2.read_secret_version(
                path='prescription-capture/mailbox'
            )
            return read_response['data']['data']
        except Exception as e:
            # Fallback to env vars for local development if Vault is unreachable
            return {
                "client_id": os.getenv("GRAPH_CLIENT_ID", "MISSING"),
                "client_secret": os.getenv("GRAPH_CLIENT_SECRET", "MISSING")
            }

    def get_database_credentials(self) -> Dict[str, str]:
        """
        Fetches Database credentials from Vault.
        Path: secret/data/prescription-capture/database
        """
        try:
            read_response = self.client.secrets.kv.v2.read_secret_version(
                path='prescription-capture/database'
            )
            return read_response['data']['data']
        except Exception:
            return {
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "postgres")
            }

    def rotate_credentials(self, credential_type: str) -> bool:
        # Placeholder for triggering Vault credential rotation if using dynamic engines
        return True

    def is_credentials_expiring_soon(self) -> bool:
        # Check Vault lease duration if using dynamic secrets
        return False

