import json
from typing import List, Optional

import httpx

from aio_meilisearch.common import request, MeiliConfig
from aio_meilisearch.types import IndexDict


async def get_all(
    meili_config: MeiliConfig, http_client: httpx.AsyncClient
) -> List[IndexDict]:
    response = await request(
        meili_config=meili_config,
        http_client=http_client,
        method="GET",
        endpoint="/indexes",
        api_key=meili_config.private_key,
    )
    js: List[IndexDict] = json.loads(response)

    return js


async def get_one(
    meili_config: MeiliConfig,
    http_client: httpx.AsyncClient,
    name: str,
    raise_404: bool = False,
) -> Optional[IndexDict]:
    try:
        return json.loads(
            await request(
                meili_config=meili_config,
                http_client=http_client,
                method="GET",
                endpoint=f"/indexes/{name}",
                api_key=meili_config.private_key,
            )
        )
    except httpx.HTTPStatusError as e:
        if not raise_404 and e.response.status_code == httpx.codes.NOT_FOUND:
            return None
        raise e


async def create_one(
    meili_config: MeiliConfig, http_client: httpx.AsyncClient, name: str, pk: str = None
) -> IndexDict:
    return json.loads(
        await request(
            meili_config=meili_config,
            http_client=http_client,
            method="POST",
            endpoint="/indexes",
            data={"uid": name, "primaryKey": pk},
            api_key=meili_config.private_key,
        )
    )


async def update_one(
    meili_config: MeiliConfig, http_client: httpx.AsyncClient, name: str, pk: str = None
) -> IndexDict:
    return json.loads(
        await request(
            meili_config=meili_config,
            http_client=http_client,
            method="PUT",
            endpoint=f"/indexes/{name}",
            data={"primaryKey": pk},
            api_key=meili_config.private_key,
        )
    )


async def delete_one(
    meili_config: MeiliConfig, http_client: httpx.AsyncClient, name: str
):
    await request(
        meili_config=meili_config,
        http_client=http_client,
        method="DELETE",
        endpoint=f"indexes/{name}",
        api_key=meili_config.private_key,
    )
