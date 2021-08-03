from aiofile import AIOFile, async_open
from loguru import logger
from pathlib import Path


class LocalStorage:
    @staticmethod
    async def save(file_name: str, second_dir: str, data: bytes, offset: int) -> None:
        path = str(Path(".").absolute())
        print(path)
        async with AIOFile(f"{path}/{second_dir}{file_name}", mode="ab") as file:
            await file.write(data, offset=offset)
            await file.fsync()
            logger.info(f"Writing in the {file_name}")

    @staticmethod
    async def get(file_name: str, second_dir: str, start: int, end: int) -> bytes:
        mediaserver_path = str(Path(".").absolute())
        full_path = f"{mediaserver_path}/{second_dir}/{file_name}"
        async with async_open(full_path, mode="rb") as file:
            file.seek(start)
            data = await file.read(end - start)
            logger.info(f"Reading file {file_name}")
            return data


storage = LocalStorage()
