from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    redis_url: str = Field(..., env="REDIS_URL")

    dev: bool = Field(..., env="DEV")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings(_env_file="../.env")
