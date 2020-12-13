import json
from typing import List, Optional

import httpx

from aio_meilisearch.common import request, MeiliConfig
from aio_meilisearch.types import IndexDict


async def get_all(meili_config: MeiliConfig) -> List[IndexDict]:
    response = await request(
        meili_config=meili_config,
        method="GET",
        endpoint="/indexes",
        api_key=meili_config.private_key,
    )
    js: List[IndexDict] = json.loads(response)

    return js


async def get_one(
    meili_config: MeiliConfig, name: str, raise_404: bool = False
) -> Optional[IndexDict]:
    try:
        return json.loads(
            await request(
                meili_config=meili_config,
                method="GET",
                endpoint=f"/indexes/{name}",
                api_key=meili_config.private_key,
            )
        )
    except httpx.HTTPStatusError as e:
        if not raise_404 and e.response.status_code == httpx.codes.NOT_FOUND:
            return None
        raise e


async def create_one(meili_config: MeiliConfig, name: str, pk: str = None) -> IndexDict:
    return json.loads(
        await request(
            meili_config=meili_config,
            method="POST",
            endpoint="/indexes",
            json={"uid": name, "primaryKey": pk},
            api_key=meili_config.private_key,
        )
    )


async def update_one(meili_config: MeiliConfig, name: str, pk: str = None) -> IndexDict:
    return json.loads(
        await request(
            meili_config=meili_config,
            method="PUT",
            endpoint=f"/indexes/{name}",
            json={"primaryKey": pk},
            api_key=meili_config.private_key,
        )
    )


async def delete_one(meili_config: MeiliConfig, name: str):
    await request(
        meili_config=meili_config,
        method="DELETE",
        endpoint=f"indexes/{name}",
        api_key=meili_config.private_key,
    )
