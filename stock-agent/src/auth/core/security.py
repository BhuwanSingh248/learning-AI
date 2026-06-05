from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta,timezone
import hashlib
import secrets

from src.auth.core.config import SECRET_KEY, ALGORITHM

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.repositories.user_repo import get_user_by_id

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

security = HTTPBearer()

# PASSWORD
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


# JWT ACCESS TOKEN
def create_access_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str):    
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def generate_refresh_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(days=30)

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials

        payload = _decode_token(token)

        user_id = int(payload["sub"])

        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )