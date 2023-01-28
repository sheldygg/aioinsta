import json

from typing import List
from ..request import RequestClient
from ..types import User, Story
from .. import config
from ..extractors import extract_story_v1

class UserClient(RequestClient):
    async def user_info_private(self, username: str):
        info = await self.private_request(method="GET", path=f"users/{username}/usernameinfo/")
        return info["json"]["user"]

    async def user_stories_private(self, user_id: int) -> List[Story]:
        params = {
            "supported_capabilities_new": json.dumps(config.SUPPORTED_CAPABILITIES)
        }
        reel = (await self.private_request(method="GET", path=f"feed/user/{user_id}/story/", params=params))["json"].get("reel")
        stories = []
        for item in reel.get("items", []):
            stories.append(extract_story_v1(item))
        return stories
    
    async def user_medias_public(self, user_id: int) -> None:
        pass
        

    async def user_stories(self, username: str) -> List[Story]:
        user_id = (await self.user_info(username)).pk
        return await self.user_stories_private(user_id)
    
    async def user_info(self, username: str) -> User:
        username = username.lower()
        user_info = await self.user_info_private(username)
        return User(**user_info)
    
    async def user_medias(self, username: str) -> None:
        username = username.lower()
        user_id = (await self.user_info(username)).pk
                