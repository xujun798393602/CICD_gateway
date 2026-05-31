"""FastAPI应用入口"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.config import settings
from src.routes import scan, report, config, notification, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    # await init_db()
    yield
    # 关闭时清理资源
    # await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="代码质量门禁系统API",
    lifespan=lifespan,
)

# 注册路由
app.include_router(scan.router, prefix="/api/v1", tags=["扫描管理"])
app.include_router(report.router, prefix="/api/v1", tags=["报告服务"])
app.include_router(config.router, prefix="/api/v1", tags=["配置管理"])
app.include_router(notification.router, prefix="/api/v1", tags=["通知服务"])
app.include_router(health.router, prefix="/api/v1", tags=["辅助接口"])
