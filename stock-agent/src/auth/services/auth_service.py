from datetime import datetime, timedelta, timezone

from src.auth.models.user import User
from src.auth.models.refresh_token import RefreshToken
from src.auth.repositories.user_repo import get_user_by_email
from src.auth.repositories.token_repo import save_token, get_token_by_hash
from src.auth.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_token
)

from src.auth.db.db import SessionLocal


# REGISTER
async def register(email: str, password: str):
    print(f"Creating a user")
    
    async with SessionLocal() as db:
        user = User(
            email=email,
            hashed_password=hash_password(password)
        )
        db.add(user)
        await db.commit()
        print("Committed")
        return user


# LOGIN
async def login(email: str, password: str):
    user = await get_user_by_email(email)

    if not user or not verify_password(password, user.hashed_password):
        raise Exception("Invalid credentials")

    access_token = create_access_token({"sub": str(user.id),  "email": user.email})

    refresh_token = generate_refresh_token(user.id)
    refresh_hash = hash_token(refresh_token)

    token_obj = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        revoked=False
    )

    await save_token(token_obj)

    return access_token, refresh_token


# REFRESH
async def refresh(refresh_token: str):
    token_hash = hash_token(refresh_token)

    token = await get_token_by_hash(token_hash)

    if not token or token.revoked:
        raise Exception("Invalid refresh token")

    if token.expires_at < datetime.utcnow():
        raise Exception("Token expired")

    return create_access_token({"sub": str(token.user_id)})