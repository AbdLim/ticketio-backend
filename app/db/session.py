from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import Settings

settings = Settings()

# Convert the database URL to async format
async_db_url = str(settings.SQLALCHEMY_DATABASE_URI).replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    async_db_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
