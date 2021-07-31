from fastapi import APIRouter, File
from fastapi.responses import JSONResponse, FileResponse, Response
import uuid
import os
from loguru import logger
from pathlib import Path
from datetime import datetime

from .schemas import FileData
from .storages import storage
from . import redis_
from . import utils


router = APIRouter()

VIDEO_ROUTE = "videos/"
IMAGE_ROUTE = "images/"


@router.post("/load_file", status_code=201, responses={409: {"model": str}})
async def load_file(
    file: FileData,
):
    """ Saves file to a correct folder and returnes it's id """

    file_id = str(uuid.uuid4().hex)
    file_extension = file.file_name.split(".")[-1]

    type = utils.get_type(file_extension)
    if type:
        await redis_.dump_data(
            file_id,
            {
                "file_name": file.file_name,
                "file_extension": file_extension,
                "file_size": file.file_size,
                "record_dt": str(datetime.now().isoformat()),
                "received_bytes": 0,
                "status": "created",
                "type": type,
            },
        )

        logger.info(f"Was created {file.file_name}")

        return {"file_id": file_id, "type": type}

    message = "File with unsupported type passed"
    logger.warning(message)
    return JSONResponse(status_code=409, content={"message": message})


@router.put("/load_file/{file_id}", status_code=200, responses={409: {"model": str}})
async def upload(
    file_id: str,
    last_byte: int,
    file_data: bytes = File(...),
):
    """
    Gets file_name and download bytes to drive with its name
    """

    logger.info(f"Recieved {len(file_data)} bytes")
    file = await redis_.load_data(file_id)

    if file["type"] == "video":
        second_dir = VIDEO_ROUTE
    else:
        second_dir = IMAGE_ROUTE

    if file["status"] == "done":
        return {"message": "Already uploaded"}

    if file["received_bytes"] + len(file_data) != last_byte:
        return {"message": "Invalid data chunk"}

    await storage.save(
        f'{file_id}.{file["file_extension"]}',
        second_dir,
        file_data,
        file["received_bytes"],
    )

    if file["received_bytes"] + len(file_data) == file["file_size"]:

        file["received_bytes"] = file["received_bytes"] + len(file_data)
        file["status"] = "done"
        await redis_.dump_data(file_id, file)

        return {"message": f"File {file['file_name']} uploaded"}

    file["received_bytes"] = file["received_bytes"] + len(file_data)
    await redis_.dump_data(file_id, file)

    return {
        "message": f"Keep going {file['received_bytes']} of {file['file_size']} for {file_id}"
    }


@router.get("/get_image", status_code=200, responses={404: {"model": str}})
async def get_file(file_id: str):
    """ Searches image with specified id and returns it """

    files_in_dir = os.listdir(IMAGE_ROUTE)
    files_in_dir = [file[:-4] for file in files_in_dir]

    dir = f"{IMAGE_ROUTE}{file_id}.jpg"
    if files_in_dir.count(file_id) != 1:
        message = "File with given id is not found"
        logger.warning(message)
        return JSONResponse(status_code=404, content={"message": message})

    return FileResponse(dir)


@router.get("/get_video")
async def get_video(file_id: str, range: str):
    """ Searches video with specified id and returns it """

    files_in_dir = os.listdir(VIDEO_ROUTE)
    files_in_dir = [file[:-4] for file in files_in_dir]

    file_name = f"{file_id}.mp4"
    if files_in_dir.count(file_id) != 1:
        message = "File with given id is not found"
        logger.warning(message)
        return JSONResponse(status_code=404, content={"message": message})

    start, end = range.split("-")
    start = int(start)
    end = int(end)

    data = await storage.get(file_name, VIDEO_ROUTE, start, end)
    filesize = str(Path(f"{VIDEO_ROUTE}{file_name}").stat().st_size)
    headers = {
        "Content-Range": f"bytes {str(start)}-{str(end)}/{filesize}",
        "Accept-Ranges": "bytes",
        "Length": f"{filesize}",
    }
    return Response(data, status_code=206, headers=headers, media_type="video/mp4")
