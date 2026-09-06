"""应用配置：通过 Pydantic Settings 读取环境变量 / .env，禁止在代码中硬编码敏感信息。"""
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，所有字段均可通过环境变量或 .env 覆盖。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 应用
    PROJECT_NAME: str = "offerAI 智能面试官"
    ENVIRONMENT: str = "dev"
    API_V1_PREFIX: str = "/api/v1"

    # 安全 / JWT
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # MySQL
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "offer_ai"
    DB_PASSWORD: str = "offer_ai_pass"
    DB_NAME: str = "offer_ai"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Dify（可选编排层，暂未启用）
    DIFY_BASE_URL: str = "http://127.0.0.1"
    DIFY_API_KEY: str = ""
    DIFY_TIMEOUT: int = 60
    DIFY_MAX_RETRIES: int = 3

    # DeepSeek（MVP 直连，OpenAI 兼容协议）
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_TIMEOUT: int = 60

    # MinIO 对象存储
    MINIO_ENDPOINT: str = "127.0.0.1:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "resume"

    @property
    def database_url(self) -> str:
        """SQLAlchemy 异步连接串（aiomysql 驱动），账号密码做 URL 编码以防特殊字符。"""
        user = quote_plus(self.DB_USER)
        pwd = quote_plus(self.DB_PASSWORD)
        return f"mysql+aiomysql://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
