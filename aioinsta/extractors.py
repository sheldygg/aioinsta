import json

from aioinsta.types.media import Media, MediaType, Photo, Resource, Video
from aioinsta.types.user import User, UserShort

MEDIA_TYPES_GQL = {
    "GraphImage": MediaType.Photo,
    "GraphVideo": MediaType.Video,
    "GraphSidecar": MediaType.Album,
    "StoryVideo": MediaType.Video,
}


def extract_user_graphql(data: dict) -> User:
    return User(
        pk=data.get("id"),
        media_count=data.get("edge_owner_to_timeline_media", {}).get("count", 0),
        follower_count=data.get("edge_followed_by", {}).get("count", 0),
        following_count=data.get("edge_follow", {}).get("count", 0),
        **data,
    )


def extract_user_v1(data: dict) -> User:
    return User(
        profile_pic_url_hd=data.get("hd_profile_pic_url_info").get("url"),
        **data,
    )


def extract_user_short(data: dict) -> UserShort:
    return UserShort(pk=data.get("id", data.get("pk")), **data)


def extract_resource_gql(data: dict) -> Resource:
    media_type = MEDIA_TYPES_GQL[data.get("__typename")]
    display_url = data.get("display_url")
    if data.get("is_video", False):
        photo = None
        video = Video(
            url=data.get("video_url"),
            preview=display_url,
            view_count=data.get("video_view_count"),
            duration=data.get("video_duration"),
        )
    else:
        video = None
        photo = Photo(url=display_url)
    return Resource(
        pk=data.get("id"),
        media_type=media_type,
        video=video,
        photo=photo
    )


def extract_caption(data: dict) -> str | None:
    try:
        caption = (
            data.get("edge_media_to_caption", {})
            .get("edges", [])[0]
            .get("node", {})
            .get("text")
        )
    except (KeyError, IndexError):
        caption = None
    return caption


def extract_media_gql(data: dict):
    user = extract_user_short(data.get("owner"))
    media_type = MEDIA_TYPES_GQL[data.get("__typename")]
    media_id = data.get("id")
    display_url = data.get("display_url")
    caption = extract_caption(data)
    if data.get("is_video", False):
        photo = None
        video = Video(
            url=data.get("video_url"),
            preview=display_url,
            view_count=data.get("video_view_count"),
            duration=data.get("video_duration"),
        )
    else:
        video = None
        photo = Photo(url=display_url)
    return Media(
        id=media_id,
        code=data.get("shortcode"),
        pk=media_id,
        taken_at=data.get("taken_at_timestamp"),
        user=user,
        caption=caption,
        media_type=media_type,
        video=video,
        photo=photo,
        resource=[
            extract_resource_gql(edge.get("node"))
            for edge in data.get("edge_sidecar_to_children", {}).get("edges", [])
        ],
    )
