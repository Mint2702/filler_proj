from fastapi import APIRouter, File, Header
from fastapi.responses import JSONResponse, FileResponse
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
OTHER_ROUTE = "other/"


@router.post("/load_file", status_code=201, responses={409: {"model": str}})
async def load_file(
    file: FileData,
):
    """ Saves file to a correct folder and returnes it's id """

    file_id = str(uuid.uuid4().hex)
    file_extension = file.file_name.split(".")[-1]

    type = utils.get_type(file_extension)
    print(type)

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
    elif file["type"] == "image":
        second_dir = IMAGE_ROUTE
    else:
        second_dir = OTHER_ROUTE

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
def get_file(file_id: str):
    """ Searches image with specified id and returns it """

    files_in_dir = os.listdir(IMAGE_ROUTE)
    files_in_dir = [file[:-4] for file in files_in_dir]

    dir = f"{IMAGE_ROUTE}{file_id}.jpg"
    if files_in_dir.count(file_id) != 1:
        message = "File with given id is not found"
        logger.warning(message)
        return JSONResponse(status_code=404, content={"message": message})

    return FileResponse(dir)


@router.get("/get_video", status_code=200, responses={404: {"model": str}})
def get_file(file_id: str, range: str = Header(None)):
    """ Searches video with specified id and returns it """

    files_in_dir = os.listdir(VIDEO_ROUTE)
    files_in_dir = [file[:-4] for file in files_in_dir]

    video_path = Path(f"{VIDEO_ROUTE}{file_id}.mp4")
    if files_in_dir.count(file_id) != 1:
        message = "File with given id is not found"
        logger.warning(message)
        return JSONResponse(status_code=404, content={"message": message})

    # start, end = range.replace("bytes=", "").split("-")
    # start = int(start)
    # end = int(end) if end else start + CHUNK_SIZE
    # with open(video_path, "rb") as video:
    #     video.seek(start)
    #     data = video.read(end - start)
    #     filesize = str(video_path.stat().st_size)
    #     headers = {
    #         'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
    #         'Accept-Ranges': 'bytes'
    #     }
    #     return Response(data, status_code=206, headers=headers, media_type="video/mp4")

    # file_like = open(video_path, mode="rb")
    # return StreamingResponse(file_like, media_type="video/mp4")

    return FileResponse(video_path)
