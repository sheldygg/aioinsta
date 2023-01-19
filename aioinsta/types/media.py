from datetime import datetime

from pydantic import BaseModel, HttpUrl
from typing import Optional
from .usershort import UserShort


class Media(BaseModel):
    media_type: str
    thumbnail_url: str
    video_url: Optional[HttpUrl] = None
    user: UserShort
    taken_at: datetime
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    caption: Optional[str] = None
    video_duration: Optional[float] = None