"""Cifrado de tokens OAuth (Fernet · cryptography). RONDA D.

OAUTH_ENCRYPTION_KEY vacía → encrypt/decrypt levantan CryptoNotConfigured → el caller
responde 503 honesto. NUNCA se guardan tokens en claro (regla de seguridad)."""
from cryptography.fernet import Fernet
from app.api.routes.oauth._oauth_config import get_oauth_settings


class CryptoNotConfigured(RuntimeError):
    """OAUTH_ENCRYPTION_KEY no seteada · no se puede cifrar/descifrar tokens."""


def _fernet() -> Fernet:
    key = get_oauth_settings().oauth_encryption_key.strip()
    if not key:
        raise CryptoNotConfigured("OAUTH_ENCRYPTION_KEY no configurada")
    return Fernet(key.encode())


def encrypt_token(plaintext: str) -> str:
    """Cifra un token a ciphertext urlsafe-base64. Lanza CryptoNotConfigured si no hay key."""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Descifra un token. Lanza CryptoNotConfigured si no hay key."""
    return _fernet().decrypt(ciphertext.encode()).decode()
