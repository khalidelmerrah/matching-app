from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/slowburn"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    SECRET_KEY: str = "dev_secret"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
