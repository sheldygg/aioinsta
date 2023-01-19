from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class UserShort(BaseModel):
    pk: str
    username: str
    full_name: Optional[str] = None
    profile_pic_url: Optional[HttpUrl]
    profile_pic_url_hd: Optional[HttpUrl]
    is_private: Optional[bool]
    is_verified: bool
    stories: List = None
