from pydantic import BaseModel
from pydantic.fields import Field


class FileData(BaseModel):
    file_name: str = Field(
        ...,
        example="video.mp4",
        description="File name for uploaded file",
    )
    file_size: int = Field(..., gt=0, example=1024, description="File size in bytes")
