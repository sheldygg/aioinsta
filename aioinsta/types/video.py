from typing import Optional

from pydantic import BaseModel, HttpUrl

from ..enums import MediaType


class Video(BaseModel):
    media_type = MediaType.VIDEO
    preview_url: Optional[HttpUrl]
    video_url: Optional[HttpUrl]
    video_duration: Optional[int]
    view_count: Optional[int]
