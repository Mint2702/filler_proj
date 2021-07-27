from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import uuid
import shutil

from loguru import logger


router = APIRouter()


@router.put("/load_file", status_code=201, responses={409: {"model": str}})
async def load_file(
    type: str,
    file_data: UploadFile = File(...),
):
    """Sends video to the mediaserver and returns it's id/url on mediaserver"""

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
