from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from aioinsta.types.user import UserShort


class MediaType(str, Enum):
    Video = "video"
    Photo = "photo"
    Album = "album"


class Video(BaseModel):
    url: str
    preview: str
    view_count: int | None = 0
    duration: float | None = 0.0


class Photo(BaseModel):
    url: str


class Resource(BaseModel):
    pk: str | int
    media_type: MediaType
    photo: Photo | None = None
    video: Video | None = None


class Media(BaseModel):
    pk: str | int
    id: str
    code: str
    user: UserShort
    caption: str | None
    taken_at: datetime
    media_type: MediaType
    photo: Photo | None = None
    video: Video | None = None
    resource: list[Resource]
