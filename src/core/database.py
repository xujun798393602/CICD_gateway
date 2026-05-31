"""数据库连接与会话管理"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional

from src.core.config import settings


class Base(DeclarativeBase):
    """ORM基类"""
    pass


# 全局引擎和会话工厂（延迟初始化）
_engine = None
_session_factory = None


def get_engine(url: Optional[str] = None):
    """获取或创建数据库引擎"""
    global _engine
    if _engine is None or url is not None:
        db_url = url or settings.database_url
        _engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory(url: Optional[str] = None):
    """获取或创建会话工厂"""
    global _session_factory
    if _session_factory is None or url is not None:
        engine = get_engine(url)
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入用）"""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库（创建表）"""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    global _engine, _session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _session_factory = None
