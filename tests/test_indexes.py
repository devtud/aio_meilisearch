import asyncio
from typing import List

import httpx

from aio_meilisearch.models import MeiliSearch, Index
from tests.utils import DockerTestCase


class TestIndexes(DockerTestCase):
    def tearDown(self) -> None:
        http_client = httpx.AsyncClient()
        meilisearch = MeiliSearch(
            meili_config=self.meili_config, http_client=http_client
        )
        loop = asyncio.get_event_loop()
        indexes = loop.run_until_complete(meilisearch.get_indexes())
        for index in indexes:
            loop.run_until_complete(meilisearch.delete_index(index.name))
        loop.run_until_complete(http_client.aclose())

    async def test_flow(self):
        async with httpx.AsyncClient() as http_client:
            meilisearch = MeiliSearch(
                meili_config=self.meili_config, http_client=http_client
            )

            response = await meilisearch.get_indexes()

            self.assertEqual(0, len(response))

            response = await meilisearch.get_index(name="books")

            self.assertIsNone(response)

            with self.assertRaises(httpx.HTTPStatusError) as ctx:
                _ = await meilisearch.get_index(name="books", raise_404=True)

            self.assertEqual(httpx.codes.NOT_FOUND, ctx.exception.response.status_code)

            index: Index = await meilisearch.create_index(name="books")

            self.assertEqual("books", index.name)
            # assert index["primaryKey"] == "id"

            index_list: List[Index] = await meilisearch.get_indexes()

            self.assertEqual(1, len(index_list))

            index: Index = await meilisearch.get_index(name="books")

            self.assertEqual("books", index._extra["uid"])

            index: Index = await meilisearch.update_index(name="books", pk="id")

            self.assertEqual("id", index._extra["primaryKey"])

            await meilisearch.delete_index(name="books")

            index_list = await meilisearch.get_indexes()

            self.assertEqual(0, len(index_list))

    async def test_default_settings(self):
        async with httpx.AsyncClient() as http_client:
            meilisearch = MeiliSearch(
                meili_config=self.meili_config, http_client=http_client
            )
            index = await meilisearch.create_index("fruits", pk="pk")
            settings = await index.get_settings()

            self.assertDictEqual(
                {
                    "synonyms": {},
                    "stopWords": [],
                    "rankingRules": [
                        "typo",
                        "words",
                        "proximity",
                        "attribute",
                        "wordsPosition",
                        "exactness",
                    ],
                    "attributesForFaceting": [],
                    "distinctAttribute": None,
                    "searchableAttributes": ["*"],
                    "displayedAttributes": ["*"],
                },
                settings,
            )
