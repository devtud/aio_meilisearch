from typing import TypedDict

import httpx

from aio_meilisearch.endpoints.documents import Index
from tests.utils import DockerTestCase


class TestDocument(DockerTestCase):
    async def test_instantiate_index(self):
        async with httpx.AsyncClient() as http_client:
            index = Index(
                name="fruits",
                meili_config=self.meili_config,
                http_client=http_client,
            )
        assert index.name == "fruits"

    async def test_get_not_found(self):
        async with httpx.AsyncClient() as http_client:
            index = Index(
                name="fruits", meili_config=self.meili_config, http_client=http_client
            )
            doc = await index.get("doc-does-not-exist")
        self.assertIsNone(doc)

    async def test_get_found(self):
        class Fruit(TypedDict):
            id: str
            name: str
            colors: str

        async with httpx.AsyncClient() as http_client:
            index = Index(
                name="fruits", meili_config=self.meili_config, http_client=http_client
            )
            index: Index[Fruit]
            await index.add_many(
                documents=[{"id": "apple", "name": "apple", "color": "red"}]
            )
            doc = await index.get("apple")
        assert doc["id"] == "apple"
