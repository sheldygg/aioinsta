from urllib.parse import urlparse
from .enums import MediaType
from .types import Media, UserShort, User


MEDIA_TYPES_GQL = {
    "GraphImage": MediaType.PHOTO,
    "GraphVideo": MediaType.VIDEO,
    "GraphSidecar": MediaType.ALBUM,
    "StoryVideo": MediaType.VIDEO,
}

def validate_external_url(cls, v):
    if v is None or (v.startswith('http') and '://' in v) or isinstance(v, str):
        return v

def excract_url_code(url: str):
    path = urlparse(url).path
    parts = [p for p in path.split("/") if p]
    return parts.pop()

def extract_user_short(data):
    data["pk"] = data.get("id", data.get("pk", None))
    return UserShort(**data)

def extract_user_gql(data):
    return User(
        pk=data["id"],
        media_count=data["edge_owner_to_timeline_media"]["count"],
        follower_count=data["edge_followed_by"]["count"],
        following_count=data["edge_follow"]["count"],
        is_business=data["is_business_account"],
        public_email=data["business_email"],
        contact_phone_number=data["business_phone_number"],
        **data,
    )

def extract_media_gql(data):
    media = {}
    media["user"] = extract_user_short(data["owner"])
    media["media_type"] = MEDIA_TYPES_GQL[data["__typename"]]
    media["thumbnail_url"] = data.get("display_resources")[-1]["src"]
    media["like_count"] = data.get("edge_media_preview_like")["count"]
    media["taken_at"] = data.get("taken_at_timestamp")
    media["view_count"] = data.get("video_view_count")
    media["video_duration"] = data.get("video_duration")
    media["video_url"] = data.get("video_url")
    if data.get("edge_media_to_caption")["edges"] != []:
        caption = data.get("edge_media_to_caption")["edges"][0]["node"]["text"]
    else:
        caption = None
    media["caption"] = caption
    return Media(
        **media
    )
