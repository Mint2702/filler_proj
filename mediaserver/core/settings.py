from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    redis_url: str = Field(..., env="REDIS_URL")
    files_folder: str = Field("/mediaserver_files", env="FILES_FOLDER")
    storage_type: str = Field("local", env="STORAGE_TYPE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings(_env_file="../.env")
