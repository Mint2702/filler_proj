from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import uuid
import shutil
import os

from loguru import logger


router = APIRouter()


@router.put("/load_file", status_code=201, responses={409: {"model": str}})
async def load_file(
    type: str,
    file_data: UploadFile = File(...),
):
    """ Saves file to a correct folder and returnes it's id """

    file_id = str(uuid.uuid4().hex)

    if type == "video":
        file_path = f"core/videos/{file_id}.mp4"
    elif type == "image":
        file_path = f"core/images/{file_id}.jpg"
    else:
        message = "Wrong type passed"
        logger.warning(message)
        return JSONResponse(status_code=409, content={"message": message})

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file_data.file, buffer)

    return {"filename": file_id}


@router.get("/get_file", status_code=200, responses={404: {"model": str}})
async def get_file(type: str, file_id: str):
    """ Searches file with specified id in the specified folder and returns it """

    if type == "video":
        file_path = f"core/videos/{file_id}.mp4"
        dir = "videos"
    elif type == "image":
        file_path = f"core/images/{file_id}.jpg"
        dir = "images"
    else:
        message = "Wrong type passed"
        logger.warning(message)
        return JSONResponse(status_code=409, content={"message": message})

    files_in_dir = os.listdir(f"core/{dir}/")
    logger.info(files_in_dir)
