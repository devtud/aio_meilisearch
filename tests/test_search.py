from typing import TypedDict, List

import httpx

from aio_meilisearch.models import MeiliSearch, Index
from tests.utils import DockerTestCase


class Fruit(TypedDict):
    id: str
    type: str
    name: str
    color: str


class TestSearch(DockerTestCase):
    async def test_search(self):

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
            meilisearch = MeiliSearch(
                meili_config=self.meili_config, http_client=http_client
            )

            index: Index[Fruit] = await meilisearch.create_index("fruits")
            await index.documents.add_many(documents=fruits)
            search_result = await index.documents.search(query="apple")

            self.assertEqual(len(fruits), len(search_result["hits"]))
