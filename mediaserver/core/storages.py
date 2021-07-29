from aiofile import AIOFile
from loguru import logger

from .settings import settings


class LocalStorage:
    @staticmethod
    async def save(file_name: str, second_dir: str, data: bytes, offset: int):
        async with AIOFile(
            f"{settings.files_folder}/{second_dir}/{file_name}", mode="ab"
        ) as file:
            await file.write(data, offset=offset)
            await file.fsync()
            logger.info(f"Writing in the {file_name}")


storage_types = {"local": LocalStorage}

storage = storage_types[settings.storage_type]()
