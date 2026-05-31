"""应用配置模块"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    # 应用配置
    APP_NAME: str = "代码质量门禁系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "quality_gate"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # 报告配置
    REPORT_PATH: str = "reports"
    REPORT_TIMEOUT: int = 60

    # 扫描配置
    SCAN_TIMEOUT: int = 600
    MAX_PARALLEL_GATES: int = 4

    # 通知配置
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # GitLab配置
    GITLAB_URL: str = ""
    GITLAB_TOKEN: str = ""

    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
