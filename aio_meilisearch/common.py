from typing import Optional, Union

import httpx


class MeiliConfig:
    def __init__(
        self,
        base_url: str,
        *,
        master_key: str = None,
        private_key: str = None,
        public_key: str = None,
    ):
        self.base_url: str = base_url.strip("/")
        self.master_key: Optional[str] = master_key
        self.private_key: Optional[str] = private_key
        self.public_key: Optional[str] = public_key


async def request(
    *,
    meili_config: MeiliConfig,
    http_client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    params: dict = None,
    data: Union[dict, list] = None,
    api_key: str = None,
) -> bytes:
    url = f"{meili_config.base_url}/{endpoint.strip('/')}"

    if not api_key:
        api_key = meili_config.public_key

    headers = {"Content-Type": "application/json", "X-Meili-API-Key": api_key}

    r = await http_client.request(
        method=method, url=url, params=params, headers=headers, json=data
    )

    r.raise_for_status()

    return r.content
