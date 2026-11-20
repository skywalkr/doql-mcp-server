from typing import Any

import httpx

from .config import Device42Settings

DICTIONARY_PATH = "/services/data/v1.0/dd/"
DOQL_PATH = "/services/data/v1.0/query/"
TOKEN_PATH = "/tauth/1.0/token/"


class Device42Client:
    def __init__(self, settings: Device42Settings) -> None:
        self._settings = settings
        auth = None
        if settings.username is not None and settings.password is not None:
            auth = (settings.username, settings.password)
        self._http = httpx.AsyncClient(
            base_url=settings.base_url,
            auth=auth,
            verify=settings.verify_ssl,
            timeout=settings.timeout,
            headers={"Accept": "application/json"},
        )

    async def __aenter__(self) -> "Device42Client":
        if self._settings.client_key is not None:
            try:
                token = await self._request_token()
            except BaseException:
                await self._http.aclose()
                raise
            self._http.headers["Authorization"] = f"Bearer {token}"
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self._http.aclose()

    async def _request_token(self) -> str:
        response = await self._http.post(
            TOKEN_PATH,
            auth=(self._settings.client_key, self._settings.client_secret),
        )
        response.raise_for_status()
        token = response.json().get("token")
        if not isinstance(token, str):
            raise RuntimeError("Device42 token response did not include a token")
        return token

    async def get_dictionary(self) -> Any:
        response = await self._http.get(DICTIONARY_PATH)
        response.raise_for_status()
        return response.json()

    async def run_doql(self, query: str, output_type: str) -> str:
        response = await self._http.get(
            DOQL_PATH,
            params={"query": query, "output_type": output_type},
        )
        response.raise_for_status()
        return response.text
