from typing import List
from unittest import IsolatedAsyncioTestCase

import docker
import httpx

from aio_meilisearch.endpoints import indexes
from aio_meilisearch.types import IndexDict
from .utils import (
    get_docker_client,
    start_meili_container,
    kill_docker_container,
    get_testing_meili_config,
)


class TestIndexes(IsolatedAsyncioTestCase):
    docker_client: docker.APIClient = None
    meili_container: dict = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.docker_client = get_docker_client()
        cls.meili_config = get_testing_meili_config()
        cls.meili_container = start_meili_container(
            docker_client=cls.docker_client, meili_config=cls.meili_config
        )

    @classmethod
    def tearDownClass(cls) -> None:
        kill_docker_container(cls.docker_client, cls.meili_container)

    async def test_flow(self):
        async with httpx.AsyncClient() as http_client:
            response = await indexes.get_all(self.meili_config, http_client=http_client)

            assert len(response) == 0

            response = await indexes.get_one(
                meili_config=self.meili_config,
                http_client=http_client,
                name="books",
            )

            assert response is None

            with self.assertRaises(httpx.HTTPStatusError) as ctx:
                _ = await indexes.get_one(
                    meili_config=self.meili_config,
                    http_client=http_client,
                    name="books",
                    raise_404=True,
                )

            assert ctx.exception.response.status_code == httpx.codes.NOT_FOUND

            index: IndexDict = await indexes.create_one(
                meili_config=self.meili_config, http_client=http_client, name="books"
            )

            assert index["uid"] == "books"
            # assert index["primaryKey"] == "id"

            index_list: List[IndexDict] = await indexes.get_all(
                meili_config=self.meili_config, http_client=http_client
            )

            assert len(index_list) == 1

            index: IndexDict = await indexes.get_one(
                meili_config=self.meili_config, http_client=http_client, name="books"
            )

            assert index["uid"] == "books"

            index: IndexDict = await indexes.update_one(
                meili_config=self.meili_config,
                http_client=http_client,
                name="books",
                pk="id",
            )

            assert index["primaryKey"] == "id"

            await indexes.delete_one(
                meili_config=self.meili_config, http_client=http_client, name="books"
            )

            index_list = await indexes.get_all(
                meili_config=self.meili_config, http_client=http_client
            )

            self.assertEqual(0, len(index_list))
