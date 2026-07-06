from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import settings

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=False, poolclass=NullPool)
    return _engine


def async_session_factory() -> AsyncSession:
    return async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)()


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
