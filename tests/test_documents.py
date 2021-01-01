from typing import TypedDict

import httpx

from aio_meilisearch.models import DocumentManager, MeiliSearch
from tests.utils import DockerTestCase


class TestDocument(DockerTestCase):
    async def test_instantiate_index(self):
        async with httpx.AsyncClient() as http_client:
            doc_manager = DocumentManager(
                index_name="fruits",
                meilisearch=MeiliSearch(
                    meili_config=self.meili_config, http_client=http_client
                ),
            )
        assert doc_manager.name == "fruits"

    async def test_get_not_found(self):
        async with httpx.AsyncClient() as http_client:
            doc_manager = DocumentManager(
                index_name="fruits",
                meilisearch=MeiliSearch(
                    meili_config=self.meili_config, http_client=http_client
                ),
            )
            doc = await doc_manager.get("doc-does-not-exist")
        self.assertIsNone(doc)

    async def test_get_found(self):
        class Fruit(TypedDict):
            id: str
            name: str
            colors: str

        async with httpx.AsyncClient() as http_client:
            doc_manager = DocumentManager(
                index_name="fruits",
                meilisearch=MeiliSearch(
                    meili_config=self.meili_config, http_client=http_client
                ),
            )
            doc_manager: DocumentManager[Fruit]
            await doc_manager.add_many(
                documents=[{"id": "apple", "name": "apple", "color": "red"}]
            )
            doc = await doc_manager.get("apple")
        assert doc["id"] == "apple"
