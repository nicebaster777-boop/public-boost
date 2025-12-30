"""Security utilities: password hashing, JWT tokens, encryption."""

from datetime import datetime, timedelta, timezone
from typing import Any

from base64 import urlsafe_b64encode
from hashlib import sha256

import bcrypt
from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.core.config import settings

# Token encryption - generate Fernet key from settings
def _get_fernet_key() -> bytes:
    """Generate Fernet key from settings encryption_key."""
    key = settings.encryption_key.encode()
    # Hash to 32 bytes and encode as base64 URL-safe
    hashed = sha256(key).digest()
    return urlsafe_b64encode(hashed)

fernet = Fernet(_get_fernet_key())


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Генерируем salt и хешируем пароль
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def encrypt_token(token: str) -> str:
    """Encrypt a token for storage."""
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a stored token."""
    return fernet.decrypt(encrypted_token.encode()).decode()

