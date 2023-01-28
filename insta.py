import asyncio

from instagrapi import Client

from config import settings

async def main():
    url = "https://www.instagram.com/p/CiyOfRaJNy_/"
    client = Client(settings=settings)
    # client.login("xaxaoao", "Odolir52?")
    user_id = client.user_id_from_username("3wishesormore")
    # medias = client.user_medias(user_id)
    print(user_id)


asyncio.run(main())
