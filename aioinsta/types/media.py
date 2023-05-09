from datetime import datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl

from aioinsta.types.user import UserShort


class MediaType(str, Enum):
    Video = "video"
    Photo = "photo"
    Album = "album"


class Resource(BaseModel):
    pk: str
    media_type: MediaType
    url: HttpUrl


class Video(BaseModel):
    url: HttpUrl
    preview: HttpUrl
    view_count: int
    duration: float


class Photo(BaseModel):
    url: HttpUrl


class Media(BaseModel):
    pk: str
    id: str
    code: str
    user: UserShort
    caption: str
    taken_at: datetime
    media_type: MediaType
    photo: Photo | None = None
    video: Video | None = None
    resource: list[Resource]
