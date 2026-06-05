from sqlalchemy import select
from src.auth.models.user import User
from src.auth.db.db import SessionLocal

async def get_user_by_email(email: str):
    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    
async def get_user_by_id(user_id: int):
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()