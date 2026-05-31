"""测试配置与夹具"""
import asyncio
import os
import pytest
import pytest_asyncio
from datetime import datetime
from typing import AsyncGenerator

# 设置测试环境变量（必须在导入src模块之前）
os.environ["DB_HOST"] = "localhost"
os.environ["DB_NAME"] = "test_db"

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from httpx import AsyncClient, ASGITransport

from src.core.database import Base, get_db, get_engine, get_session_factory
from src.models import ScanTask, ScanResult, IssueDetail, GateConfig, NotificationLog


# 使用SQLite进行测试（内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_engine) -> AsyncGenerator[AsyncClient, None]:
    """创建测试HTTP客户端"""
    from src.main import app

    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_scan_task(db_session: AsyncSession):
    """创建示例扫描任务"""
    task = ScanTask(
        scan_id="scan_20260531_abc123",
        project_id="proj_001",
        project_name="测试项目A",
        project_url="https://gitlab.example.com/proj_001",
        trigger_type="push",
        trigger_ref="main",
        trigger_user="user_dev1",
        commit_sha="abc123def456",
        scan_status="pending",
        total_gates=4,
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def sample_scan_result(db_session: AsyncSession, sample_scan_task):
    """创建示例扫描结果"""
    result = ScanResult(
        scan_id=sample_scan_task.scan_id,
        gate_type="vulnerability",
        gate_name="代码漏洞扫描",
        gate_version="1.0.0",
        execution_status="completed",
        gate_result="failed",
        total_issues=2,
        critical_issues=1,
        high_issues=1,
        scanned_files=10,
        total_lines=1000,
        started_at=datetime(2026, 5, 31, 10, 0, 0),
        completed_at=datetime(2026, 5, 31, 10, 5, 0),
        duration_seconds=300,
    )
    db_session.add(result)
    await db_session.commit()
    await db_session.refresh(result)
    return result


@pytest_asyncio.fixture
async def sample_gate_config(db_session: AsyncSession):
    """创建示例门禁配置"""
    config = GateConfig(
        config_id="cfg_global_vulnerability",
        project_id=None,
        gate_type="vulnerability",
        gate_name="代码漏洞扫描",
        enabled=True,
        severity_threshold="high",
        timeout_seconds=300,
        config_data={"rules_source": "owasp", "languages": ["java", "python"]},
        script_path="scripts/vulnerability-scan.sh",
        execution_order=100,
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)
    return config
