import asyncio
import json
from typing import Generic, Optional, List, Union, Literal, TypeVar

import httpx
from httpx import HTTPStatusError

from aio_meilisearch.common import MeiliConfig, request
from aio_meilisearch.types import UpdateDict, SearchResponse, IndexDict

T = TypeVar("T")


class DocumentManager(Generic[T]):
    def __init__(self, index_name: str, meilisearch: "MeiliSearch"):
        self.name: str = index_name
        self.meili_config: MeiliConfig = meilisearch.meili_config
        self.http_client: httpx.AsyncClient = meilisearch.http_client

    async def get(self, document_id: str) -> Optional[T]:
        try:
            response = await request(
                meili_config=self.meili_config,
                http_client=self.http_client,
                method="GET",
                endpoint=f"/indexes/{self.name}/documents/{document_id}",
            )
        except HTTPStatusError as e:
            if e.response.status_code == httpx.codes.NOT_FOUND:
                return None
            raise e

        return json.loads(response)

    async def get_many(
        self, offset: int = None, limit: int = None, attrs_to_retrieve: List[str] = None
    ):
        params = {
            "offset": offset,
            "limit": limit,
            "attributesToRetrieve": attrs_to_retrieve,
        }

        return json.loads(
            await request(
                meili_config=self.meili_config,
                http_client=self.http_client,
                method="GET",
                endpoint=f"/indexes/{self.name}/documents",
                params=params,
            )
        )

    async def add_many(self, documents: List[T], overwrite_existing: bool = True):
        if overwrite_existing:
            method = "POST"
        else:
            method = "PUT"

        response = await request(
            meili_config=self.meili_config,
            http_client=self.http_client,
            method=method,
            endpoint=f"/indexes/{self.name}/documents",
            data=documents,
            api_key=self.meili_config.private_key,
        )

        update: UpdateDict = json.loads(response)

        await self._get_finished_update(update["updateId"])

    async def _get_update(self, update_id: str) -> UpdateDict:
        return json.loads(
            await request(
                meili_config=self.meili_config,
                http_client=self.http_client,
                method="GET",
                endpoint=f"/indexes/{self.name}/updates/{update_id}",
                api_key=self.meili_config.private_key,
            )
        )

    async def _get_finished_update(self, update_id) -> UpdateDict:
        while True:
            update = await self._get_update(update_id)
            if update["status"] == "processed":
                return update
            if update["status"] == "failed":
                raise Exception("Updated failed")
            await asyncio.sleep(0.25)

    async def delete_all(self):
        await self._delete_documents("all")

    async def delete_one(self, document_id: str):
        await self._delete_documents([document_id])

    async def delete_many(self, document_ids: List[str]):
        await self._delete_documents(document_ids)

    async def _delete_documents(self, documents: Union[List[str], Literal["all"]]):
        data = None
        if documents == "all":
            method = "DELETE"
            endpoint = f"/indexes/{self.name}/documents"
        elif len(documents) == 1:
            method = "DELETE"
            endpoint = f"/indexes/{self.name}/documents/{documents[0]}"
        else:
            method = "POST"
            endpoint = f"/indexes/{self.name}/documents/delete-batch"
            data = documents
        response = await request(
            meili_config=self.meili_config,
            http_client=self.http_client,
            method=method,
            endpoint=endpoint,
            data=data,
        )

        update: UpdateDict = json.loads(response)

        await self._get_finished_update(update_id=update["updateId"])

    async def search(
        self,
        query: str,
        offset: int = None,
        limit: int = None,
        filters: str = None,
        facet_filters: List[Union[str, List[str]]] = None,
        facet_distribution: List[str] = None,
        attrs_to_retrieve: List[str] = None,
        attrs_to_crop: List[str] = None,
        crop_len: int = None,
        attrs_to_highlight: List[str] = None,
        matches: bool = None,
    ) -> SearchResponse[T]:
        resp_bytes = await request(
            meili_config=self.meili_config,
            http_client=self.http_client,
            method="POST",
            endpoint=f"/indexes/{self.name}/search",
            data={
                "q": query,
                "offset": offset,
                "limit": limit,
                "filters": filters,
                "facetFilters": facet_filters,
                "facetsDistribution": facet_distribution,
                "attributesToRetrieve": attrs_to_retrieve,
                "attributesToCrop": attrs_to_crop,
                "cropLength": crop_len,
                "attributesToHighlight": attrs_to_highlight,
                "matches": matches,
            },
        )
        return json.loads(resp_bytes)


class Index(Generic[T]):
    def __init__(self, name: str, meilisearch: "MeiliSearch", extra: IndexDict = None):
        self.name = name
        self._meilisearch = meilisearch
        self._extra: Optional[IndexDict] = extra
        self._documents: Optional[DocumentManager[T]] = None

    @property
    def documents(self) -> DocumentManager[T]:
        if self._documents is None:
            self._documents: DocumentManager[T] = DocumentManager(
                index_name=self.name, meilisearch=self._meilisearch
            )
        return self._documents


class MeiliSearch:
    def __init__(self, meili_config: MeiliConfig, http_client: httpx.AsyncClient):
        self.meili_config = meili_config
        self.http_client = http_client

    async def get_indexes(
        self,
    ) -> List[Index]:
        response = await request(
            meili_config=self.meili_config,
            http_client=self.http_client,
            method="GET",
            endpoint="/indexes",
            api_key=self.meili_config.private_key,
        )
        js: List[IndexDict] = json.loads(response)

        return [Index(name=index_dict["uid"], meilisearch=self) for index_dict in js]

    async def get_index(self, name: str, raise_404: bool = False) -> Optional[Index]:
        try:
            index_dict: IndexDict = json.loads(
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
        return Index(name=index_dict["uid"], meilisearch=self, extra=index_dict)

    async def create_index(self, name: str, pk: str = None) -> Index:
        index_dict: IndexDict = json.loads(
            await request(
                meili_config=self.meili_config,
                http_client=self.http_client,
                method="POST",
                endpoint="/indexes",
                data={"uid": name, "primaryKey": pk},
                api_key=self.meili_config.private_key,
            )
        )
        return Index(name=index_dict["uid"], meilisearch=self, extra=index_dict)

    async def update_index(self, name: str, pk: str = None) -> Index:
        index_dict: IndexDict = json.loads(
            await request(
                meili_config=self.meili_config,
                http_client=self.http_client,
                method="PUT",
                endpoint=f"/indexes/{name}",
                data={"primaryKey": pk},
                api_key=self.meili_config.private_key,
            )
        )
        return Index(name=index_dict["uid"], meilisearch=self, extra=index_dict)

    async def delete_index(self, name: str):
        await request(
            meili_config=self.meili_config,
            http_client=self.http_client,
            method="DELETE",
            endpoint=f"indexes/{name}",
            api_key=self.meili_config.private_key,
        )
