from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel

from .photo import Photo
from .usershort import UserShort
from .video import Video


class Media(BaseModel):
    media_type: str
    thumbnail_url: str
    photo: Optional[Photo]
    video: Optional[Video]
    user: UserShort
    taken_at: datetime
    like_count: Optional[int] = None
    caption: Optional[str] = None
    album: Optional[List[Union[Photo, Video]]]

    class Config:
        smart_union = True
