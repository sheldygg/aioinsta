from enum import Enum


class MediaType(str, Enum):
    VIDEO = "Video"
    PHOTO = "Photo"
    IGTV = "IGTV"
    REEL = "Reel"
    ALBUM = "Album"
