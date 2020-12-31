from typing import TypedDict, List

import httpx

from aio_meilisearch.endpoints.documents import Index
from aio_meilisearch.types import SearchResponse
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

    async def test_search(self):
        class Fruit(TypedDict):
            id: str
            type: str
            name: str
            color: str

        fruits: List[Fruit] = [
            {"id": "id1", "type": "apple", "name": "Pink Pearl", "color": "pink"},
            {"id": "id2", "type": "apple", "name": "Ambrosia", "color": "red"},
            {"id": "id3", "type": "apple", "name": "Redlove Apples", "color": "red"},
            {"id": "id4", "type": "apple", "name": "Macoun Apple", "color": "red"},
            {"id": "id5", "type": "apple", "name": "Grimes Golden", "color": "yellow"},
            {"id": "id6", "type": "apple", "name": "Opal", "color": "yellow"},
            {
                "id": "id7",
                "type": "apple",
                "name": "Golden Delicious",
                "color": "yellow",
            },
        ]

        async with httpx.AsyncClient() as http_client:
            index: Index[Fruit] = Index(
                name="fruits", meili_config=self.meili_config, http_client=http_client
            )
            await index.add_many(documents=fruits)
            search_result: SearchResponse = await index.search(query="apple")
            self.assertEqual(len(fruits), len(search_result["hits"]))
