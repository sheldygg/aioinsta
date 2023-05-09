import json

from aioinsta import login


class ChallengeClient:
    def __init__(self, login_client: "login.Login"):
        self.login_client = login_client

    async def resolve_challenge(self, response: dict):
        challenge_url = response["challenge"]["api_path"]
        user_id, nonce_code = challenge_url.split("/")[2:4]
        challenge_context = response.get("challenge", {}).get("challenge_context")
        if not challenge_context:
            challenge_context = json.dumps(
                {
                    "step_name": "",
                    "nonce_code": nonce_code,
                    "user_id": int(user_id),
                    "is_stateless": False,
                }
            )
        params = {
            "guid": self.login_client.uuid,
            "device_id": self.login_client.android_device_id,
            "challenge_context": challenge_context,
        }
        response = await self.login_client.private_request(
            method="GET",
            path=challenge_url[1:],
            params=params,
        )
        return response
