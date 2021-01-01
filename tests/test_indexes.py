from typing import List

import httpx

from aio_meilisearch.endpoints.indexes import MeiliSearch
from aio_meilisearch.types import IndexDict
from tests.utils import DockerTestCase


class TestIndexes(DockerTestCase):
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

            index: IndexDict = await meilisearch.create_index(name="books")

            self.assertEqual("books", index["uid"])
            # assert index["primaryKey"] == "id"

            index_list: List[IndexDict] = await meilisearch.get_indexes()

            self.assertEqual(1, len(index_list))

            index: IndexDict = await meilisearch.get_index(name="books")

            self.assertEqual("books", index["uid"])

            index: IndexDict = await meilisearch.update_index(name="books", pk="id")

            self.assertEqual("id", index["primaryKey"])

            await meilisearch.delete_index(name="books")

            index_list = await meilisearch.get_indexes()

            self.assertEqual(0, len(index_list))
