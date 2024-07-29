import os

import config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base


# from dotenv import find_dotenv, load_dotenv
#
# load_dotenv(find_dotenv())

# engine = create_async_engine(os.getenv('DB_LITE'), echo=True)
engine = create_async_engine(config.DB_LITE, echo=True)


session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# это слишком некрасивый и не удобный вариант
# async def m():
#     async with session_maker() as session:
#         session.execute()

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)