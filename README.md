# aioINSTA

# Still in development

# Asynchronous wrapper of instagram PRIVATE API

```python
import asyncio
from aioinsta import Client

settings = {"your_settings": "xxxx"}
client = Client()

async def main():
    await client.login("username", "password")
    data = await client.media_info(
        client.media_pk_from_url("https://www.instagram.com/p/CrfF1nhslH4")
    )
    print(data)
    
asyncio.run(main())
```