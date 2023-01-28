from typing import Optional

from pydantic import BaseModel, HttpUrl

from ..enums import MediaType


class Photo(BaseModel):
    media_type = MediaType.PHOTO
    photo_url: Optional[HttpUrl]
