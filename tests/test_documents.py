from asyncio import AbstractEventLoop
from typing import TypedDict
from unittest import IsolatedAsyncioTestCase

import docker
import httpx

from aio_meilisearch.common import MeiliConfig
from aio_meilisearch.endpoints.documents import Index
from tests.utils import (
    get_docker_client,
    get_testing_meili_config,
    start_meili_container,
    kill_docker_container,
)


class TestDocument(IsolatedAsyncioTestCase):
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
