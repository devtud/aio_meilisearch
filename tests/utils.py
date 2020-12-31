import uuid
from time import sleep
from unittest.async_case import IsolatedAsyncioTestCase

import docker

from aio_meilisearch.common import MeiliConfig


def get_testing_master_key() -> str:
    return "testing_master_key"


def get_testing_meili_config() -> MeiliConfig:
    return MeiliConfig(
        base_url="http://localhost:7700",
        master_key=get_testing_master_key(),
        public_key="f73de51409783324e3a6a4976cca4fe963d39e6a128baa4bbb7bd76afc211255",
        private_key="fe05daa57f600b3174431a6b827e9c821efca9cc90e16219c40b5764d860c40a",
    )


def get_docker_client() -> docker.APIClient:
    # base url is the unix socket we use to communicate with docker
    return docker.APIClient(base_url="unix://var/run/docker.sock", version="auto")


def start_meili_container(
    docker_client: docker.APIClient, meili_config: MeiliConfig
) -> dict:
    """
    Use docker to spin up a Meilisearch container for the duration of the testing session.
    Kill it as soon as all tests are run.
    DB actions persist across the entirety of the testing session.
    """
    # pull image from docker
    image = "getmeili/meilisearch:v0.17.0"
    docker_client.pull(image)

    # create the new container using
    # the same image used by our database
    container = docker_client.create_container(
        image=image,
        name=f"test-meilisearch-{uuid.uuid4()}",
        detach=True,
        environment={
            "MEILI_ENV": "production",
            "MEILI_NO_ANALYTICS": "true",
            "MEILI_MASTER_KEY": meili_config.master_key,
        },
        ports=[7700],
        # hostname="0.0.0.0",
        host_config=docker_client.create_host_config(
            port_bindings={7700: 7700}, publish_all_ports=True
        ),
    )
    docker_client.start(container=container["Id"])

    return container


def kill_docker_container(docker_client: docker.APIClient, container: dict):
    docker_client.kill(container["Id"])
    docker_client.remove_container(container["Id"])


class DockerTestCase(IsolatedAsyncioTestCase):
    docker_client: docker.APIClient = None
    meili_container: dict = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.docker_client = get_docker_client()
        cls.meili_config = get_testing_meili_config()
        cls.meili_container = start_meili_container(
            docker_client=cls.docker_client, meili_config=cls.meili_config
        )
        sleep(1)

    @classmethod
    def tearDownClass(cls) -> None:
        kill_docker_container(cls.docker_client, cls.meili_container)
