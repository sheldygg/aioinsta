from urllib.parse import urlparse

from .enums import MediaType
from .types import Media, Photo, UserShort, Video, Story, StoryMedia

MEDIA_TYPES_GQL = {
    "GraphImage": MediaType.PHOTO,
    "GraphVideo": MediaType.VIDEO,
    "GraphSidecar": MediaType.ALBUM,
    "StoryVideo": MediaType.VIDEO,
}

MEDIA_TYPES_V1 = {
    1: MediaType.PHOTO,
    2: MediaType.VIDEO
}

def excract_url_code(url: str):
    path = urlparse(url).path
    parts = [p for p in path.split("/") if p]
    return parts.pop()


def extract_user_short(data):
    data["pk"] = data.get("id", data.get("pk", None))
    return UserShort(**data)


def exctract_album(data):
    album = []
    for album_media in data:
        media_data = album_media["node"]
        media_type = MEDIA_TYPES_GQL[media_data["__typename"]]
        if media_type == MediaType.PHOTO:
            album.append(Photo(photo_url=media_data.get("display_url")))
        elif media_type == MediaType.VIDEO:
            album.append(
                Video(
                    preview_url=media_data.get("display_url"),
                    video_url=media_data.get("video_url"),
                    view_count=media_data.get("video_view_count"),
                )
            )
    return album


def extract_media_gql(data):
    if data.get("edge_media_to_caption")["edges"] != []:
        caption = data.get("edge_media_to_caption")["edges"][0]["node"]["text"]
    else:
        caption = None
    resources = data.get("edge_sidecar_to_children")
    if resources:
        album = exctract_album(resources.get("edges"))
    else:
        album = None
    return Media(
        media_type=MEDIA_TYPES_GQL[data["__typename"]],
        user=extract_user_short(data["owner"]),
        thumbnail_url=data.get("display_resources")[-1]["src"],
        taken_at=data.get("taken_at_timestamp"),
        photo=Photo(photo_url=data.get("display_resources")[-1]["src"]),
        video=Video(
            video_url=data.get("video_url"),
            video_duration=data.get("video_duration"),
            view_count=data.get("video_view_count"),
            preview_url=data.get("display_resources")[-1]["src"],
        ),
        caption=caption,
        like_count=data.get("edge_media_preview_like")["count"],
        album=album,
    )

def extract_story_v1(data):
    thumbnail_url = data.get("image_versions2").get("candidates")[0]["url"]
    if "video_versions" in data:
        video_url = data.get("video_versions")[0]["url"]
        video = Video(preview_url=thumbnail_url, video_url=video_url)
        video_duration = data["video_duration"]
    else:
        video = None
        video_duration = None
    feed_medias = []
    story_feed_medias = data.get('story_feed_media') or []
    for feed_media in story_feed_medias:
        feed_media["media_pk"] = int(feed_media["media_id"])
        feed_medias.append(StoryMedia(**feed_media))
    return Story(
        pk=data["pk"],
        id=data["id"],
        code=data["code"],
        video=video,
        video_duration=video_duration,
        media_type=MEDIA_TYPES_V1[data["media_type"]],
        taken_at=data["taken_at"],
        user=extract_user_short(data["user"]),
        medias=feed_medias
    )
