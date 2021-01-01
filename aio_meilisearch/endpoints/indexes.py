import json
from typing import List, Optional

import httpx

from aio_meilisearch.common import request, MeiliConfig
from aio_meilisearch.types import IndexDict


class MeiliSearch:
    def __init__(self, meili_config: MeiliConfig, http_client: httpx.AsyncClient):
        self.meili_config = meili_config
        self.http_client = http_client

    async def get_indexes(
        self,
    ) -> List[IndexDict]:
        response = await request(
            meili_config=self.meili_config,
            http_client=self.http_client,
            method="GET",
            endpoint="/indexes",
            api_key=self.meili_config.private_key,
        )
        js: List[IndexDict] = json.loads(response)

        return js

    async def get_index(
        self, name: str, raise_404: bool = False
    ) -> Optional[IndexDict]:
        try:
            return json.loads(
                await request(
                    meili_config=self.meili_config,
                    http_client=self.http_client,
                    method="GET",
                    endpoint=f"/indexes/{name}",
                    api_key=self.meili_config.private_key,
                )
            )
        except httpx.HTTPStatusError as e:
            if not raise_404 and e.response.status_code == httpx.codes.NOT_FOUND:
                return None
            raise e

    async def create_index(self, name: str, pk: str = None) -> IndexDict:
        return json.loads(
            await request(
                meili_config=self.meili_config,
                http_client=self.http_client,
                method="POST",
                endpoint="/indexes",
                data={"uid": name, "primaryKey": pk},
                api_key=self.meili_config.private_key,
            )
        )

    async def update_index(self, name: str, pk: str = None) -> IndexDict:
        return json.loads(
            await request(
                meili_config=self.meili_config,
                http_client=self.http_client,
                method="PUT",
                endpoint=f"/indexes/{name}",
                data={"primaryKey": pk},
                api_key=self.meili_config.private_key,
            )
        )

    async def delete_index(self, name: str):
        await request(
            meili_config=self.meili_config,
            http_client=self.http_client,
            method="DELETE",
            endpoint=f"indexes/{name}",
            api_key=self.meili_config.private_key,
        )
