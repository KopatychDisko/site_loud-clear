from sqlalchemy import select

from model import Executors

async def get_executor(session, uuid: str):
    result = await session.execute(select(Executors).where(Executors.id == uuid))
    return result.scalar_one_or_none()

async def get_executors(session, limit: int = 12):
    result = await session.execute(select(Executors).limit(limit))
    return result.scalars().all()