"""
JWT Authentication — token creation, password hashing.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import hashlib
import base64
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-long-random-string-32chars-min")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days

# Use sha256_crypt instead of bcrypt to avoid the 72-byte password limit
# sha256_crypt has no password length restriction and is very secure
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def _prepare_password(password: str) -> str:
    """
    Pre-hash password with SHA-256 then base64-encode.
    This avoids bcrypt's 72-byte limit while keeping full password entropy.
    (Standard approach used by many auth libraries)
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("utf-8")


def hash_password(password: str) -> str:
    return pwd_context.hash(_prepare_password(password))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_prepare_password(plain), hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
