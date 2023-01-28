from datetime import datetime

from pydantic import BaseModel
from typing import Optional, List

from .usershort import UserShort
from .photo import Photo
from .video import Video

class StoryMedia(BaseModel):
    x: float = 0.5
    y: float = 0.4997396
    z: float = 0
    width: float = 0.8
    height: float = 0.60572916
    rotation: float = 0.0
    is_pinned: Optional[bool]
    is_hidden: Optional[bool]
    is_sticker: Optional[bool]
    is_fb_sticker: Optional[bool]
    media_pk: int
    user_id: Optional[int]
    product_type: Optional[str]
    media_code: Optional[str]

class Story(BaseModel):
    pk: int
    id: str
    code: str
    taken_at: datetime
    media_type: str
    photo: Optional[Photo]
    video: Optional[Video]
    user: UserShort
    video_duration: Optional[int]
    # video_url: Optional[HttpUrl]
    # video_duration: Optional[float]
    # sponsor_tags: List[UserShort]
    # mentions: List[StoryMention]
    # links: List[StoryLink]
    # hashtags: List[StoryHashtag]
    # locations: List[StoryLocation]
    # stickers: List[StorySticker]
    medias: List[StoryMedia] = None

