from pydantic import BaseModel


class User(BaseModel):
    pk: str | int
    username: str
    full_name: str
    is_private: bool
    profile_pic_url: str
    profile_pic_url_hd: str | None = None
    is_verified: bool
    media_count: int
    follower_count: int
    following_count: int
    biography: str | None = None


class UserShort(BaseModel):
    pk: str
    username: str
    full_name: str | None = ""
    profile_pic_url: str | None = None
    profile_pic_url_hd: str | None = None
    is_private: bool | None
    stories: list = []
