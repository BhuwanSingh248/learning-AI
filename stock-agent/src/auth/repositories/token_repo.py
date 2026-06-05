from sqlalchemy import select
from src.auth.models.refresh_token import RefreshToken
from src.auth.db.db import SessionLocal

async def save_token(token_obj):
    async with SessionLocal() as db:
        db.add(token_obj)
        await db.commit()


async def get_token_by_hash(token_hash: str):
    async with SessionLocal() as db:
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()