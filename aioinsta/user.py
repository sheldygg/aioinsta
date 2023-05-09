from aioinsta import login
from aioinsta.extractors import extract_user_graphql, extract_user_v1
from aioinsta.types.user import User


class UserClient:
    def __init__(self, login_client: "login.Login"):
        self.login_client = login_client

    async def user_info_by_username_gql(self, username: str) -> User:
        response = await self.login_client.public_a1_request(
            method="GET", path=f"/{username!s}/"
        )
        user = extract_user_graphql(response.get("user"))
        return user

    async def user_info_by_username_v1(self, username: str) -> User:
        response = (
            await self.login_client.private_request(
                method="GET", path=f"users/{username}/usernameinfo"
            )
        ).get("response")
        return extract_user_v1(response.get("user"))

    async def user_info_from_username(self, username: str) -> User | None:
        username = str(username).lower()
        try:
            return await self.user_info_by_username_gql(username)
        except ValueError:
            return await self.user_info_by_username_v1(username)

    async def user_id_from_username(self, username: str):
        return (await self.user_info_from_username(username)).pk
