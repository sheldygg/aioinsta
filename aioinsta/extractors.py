import json

from aioinsta.types.media import Media, MediaType, Photo, Resource, Video
from aioinsta.types.user import User, UserShort

MEDIA_TYPES_GQL = {
    "GraphImage": MediaType.Photo,
    "GraphVideo": MediaType.Video,
    "GraphSidecar": MediaType.Album,
    "StoryVideo": MediaType.Video,
}

MEDIA_TYPES_V1 = {
    8: MediaType.Album,
    2: MediaType.Video,
    1: MediaType.Photo,
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
    data["pk"] = data.get("id", data.get("pk", None))
    return UserShort(**data)


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


def extract_resource_v1(data: dict) -> Resource:
    media_type = MEDIA_TYPES_V1[data.get("media_type")]
    thumbnail_url = sorted(
        data["image_versions2"]["candidates"],
        key=lambda o: o["height"] * o["width"],
    )[-1]["url"]
    if media_type == MediaType.Video:
        photo = None
        video_url = sorted(
            data["video_versions"], key=lambda o: o["height"] * o["width"]
        )[-1]["url"]
        video = Video(
            url=video_url,
            preview=thumbnail_url,
            view_count=data.get("video_view_count"),
            duration=data.get("video_duration"),
        )
    else:
        video = None
        photo = Photo(url=thumbnail_url)
    return Resource(
        pk=data.get("pk"),
        media_type=media_type,
        photo=photo,
        video=video
    )


def extract_media_v1(data: dict):
    media_id = data.get("id")
    user = extract_user_short(data.get("user"))
    media_type = MEDIA_TYPES_V1[data.get("media_type")]
    caption = data.get("caption", {}).get("text")
    if media_type == MediaType.Video:
        video_url = sorted(
            data["video_versions"], key=lambda o: o["height"] * o["width"]
        )[-1]["url"]
        thumbnail_url = sorted(
            data["image_versions2"]["candidates"],
            key=lambda o: o["height"] * o["width"],
        )[-1]["url"]
        photo = None
        video = Video(
            url=video_url,
            preview=thumbnail_url,
            view_count=data.get("play_count"),
            duration=data.get("video_duration")

        )
    elif media_type == MediaType.Photo:
        video = None
        thumbnail_url = sorted(
            data["image_versions2"]["candidates"],
            key=lambda o: o["height"] * o["width"],
        )[-1]["url"]
        photo = Photo(
            url=thumbnail_url
        )
    else:
        video = None
        photo = None
    return Media(
        pk=media_id,
        id=media_id,
        code=data.get("id"),
        user=user,
        video=video,
        photo=photo,
        taken_at=data.get("taken_at"),
        media_type=media_type,
        caption=caption,
        resource=[extract_resource_v1(carousel) for carousel in data.get("carousel_media", [])]
    )
