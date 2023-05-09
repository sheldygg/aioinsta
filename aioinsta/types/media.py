from datetime import datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl

from aioinsta.types.user import UserShort


class MediaType(str, Enum):
    Video = "video"
    Photo = "photo"
    Album = "album"


class Video(BaseModel):
    url: HttpUrl
    preview: HttpUrl
    view_count: int
    duration: float | None = 0.0


class Photo(BaseModel):
    url: HttpUrl


class Resource(BaseModel):
    pk: str
    media_type: MediaType
    photo: Photo | None = None
    video: Video | None = None


class Media(BaseModel):
    pk: str
    id: str
    code: str
    user: UserShort
    caption: str | None
    taken_at: datetime
    media_type: MediaType
    photo: Photo | None = None
    video: Video | None = None
    resource: list[Resource]
