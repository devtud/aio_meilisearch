import asyncio
import uuid
from time import sleep
from unittest.async_case import IsolatedAsyncioTestCase

import docker
import httpx
from docker.models.containers import Container

from aio_meilisearch.common import MeiliConfig
from aio_meilisearch.models import MeiliSearch

MEILISEARCH_DOCKER_IMAGE = "getmeili/meilisearch:v0.17.0"


def get_testing_master_key() -> str:
    return "testing_master_key"


def get_testing_meili_config() -> MeiliConfig:
    return MeiliConfig(
        base_url="http://localhost:7700",
        master_key=get_testing_master_key(),
        public_key="f73de51409783324e3a6a4976cca4fe963d39e6a128baa4bbb7bd76afc211255",
        private_key="fe05daa57f600b3174431a6b827e9c821efca9cc90e16219c40b5764d860c40a",
    )


def get_docker_client() -> docker.DockerClient:
    return docker.DockerClient(base_url="unix://var/run/docker.sock", version="auto")


def start_meili_container(
    meili_config: MeiliConfig, docker_base_url: str = "unix://var/run/docker.sock"
) -> Container:
    docker_client = docker.DockerClient(base_url=docker_base_url, version="auto")

    docker_client.api.pull(MEILISEARCH_DOCKER_IMAGE)

    container: Container = docker_client.containers.create(
        image=MEILISEARCH_DOCKER_IMAGE,
        name=f"test-meilisearch-{uuid.uuid4()}",
        detach=True,
        ports={7700: 7700},
        environment={
            "MEILI_ENV": "production",
            "MEILI_NO_ANALYTICS": "true",
            "MEILI_MASTER_KEY": meili_config.master_key,
        },
    )
    container.start()

    return container


class DockerTestCase(IsolatedAsyncioTestCase):

    meili_container: Container = None

    @classmethod
    def setUpClass(cls) -> None:
        """ Before each test class create meili container """
        cls.meili_config = get_testing_meili_config()
        cls.meili_container = start_meili_container(meili_config=cls.meili_config)
        sleep(1)

    @classmethod
    def tearDownClass(cls) -> None:
        """ After each test class destroy the container"""
        cls.meili_container.kill()
        cls.meili_container.remove()
        cls.meili_container.client.close()

    def setUp(self) -> None:
        self.maxDiff = None

    def tearDown(self) -> None:
        """ After each test method remove all indexes from meili db"""
        http_client = httpx.AsyncClient()
        meilisearch = MeiliSearch(
            meili_config=self.meili_config, http_client=http_client
        )
        loop = asyncio.get_event_loop()
        indexes = loop.run_until_complete(meilisearch.get_indexes())
        for index in indexes:
            loop.run_until_complete(meilisearch.delete_index(index.name))
        loop.run_until_complete(http_client.aclose())
