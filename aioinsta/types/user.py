from pydantic import BaseModel, HttpUrl
from typing import Optional

class User(BaseModel):
    pk: int
    username: str
    full_name: str
    is_private: bool
    profile_pic_url: HttpUrl
    profile_pic_url_hd: Optional[HttpUrl]
    is_verified: bool
    media_count: int
    follower_count: int
    following_count: int
    biography: Optional[str] = ""
    external_url: Optional[str]
    account_type: Optional[int]
    is_business: bool

    public_email: Optional[str]
    contact_phone_number: Optional[str]
    public_phone_country_code: Optional[str]
    public_phone_number: Optional[str]
    business_contact_method: Optional[str]
    business_category_name: Optional[str]
    category_name: Optional[str]
    category: Optional[str]

    address_street: Optional[str]
    city_id: Optional[str]
    city_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    zip: Optional[str]
    instagram_location_id: Optional[str]
    interop_messaging_user_fbid: Optional[str]