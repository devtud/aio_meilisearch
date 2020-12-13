import asyncio
import uuid
import warnings

import docker as py_docker
import httpx
import pytest

from aio_meilisearch.common import MeiliConfig


@pytest.fixture(scope="session")
def loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.get_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
def testing_http_client(loop: asyncio.AbstractEventLoop) -> httpx.AsyncClient:
    client = httpx.AsyncClient()
    try:
        yield client
    finally:
        loop.run_until_complete(client.aclose())


@pytest.fixture(scope="session")
def testing_master_key() -> str:
    return "testing_master_key"


@pytest.fixture(scope="session")
def testing_meili_config(
    testing_http_client: httpx.AsyncClient, testing_master_key: str
) -> MeiliConfig:
    return MeiliConfig(
        http_client=testing_http_client,
        base_url="http://localhost:7700",
        master_key=testing_master_key,
        public_key="f73de51409783324e3a6a4976cca4fe963d39e6a128baa4bbb7bd76afc211255",
        private_key="fe05daa57f600b3174431a6b827e9c821efca9cc90e16219c40b5764d860c40a",
    )


@pytest.fixture(scope="session")
def docker() -> py_docker.APIClient:
    # base url is the unix socket we use to communicate with docker
    return py_docker.APIClient(base_url="unix://var/run/docker.sock", version="auto")


@pytest.fixture(scope="session", autouse=True)
def meili_container(
    docker: py_docker.APIClient, testing_meili_config: MeiliConfig
) -> None:
    """
    Use docker to spin up a Meilisearch container for the duration of the testing session.
    Kill it as soon as all tests are run.
    DB actions persist across the entirety of the testing session.
    """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    # pull image from docker
    image = "getmeili/meilisearch:v0.17.0"
    docker.pull(image)

    # create the new container using
    # the same image used by our database
    container = docker.create_container(
        image=image,
        name=f"test-meilisearch-{uuid.uuid4()}",
        detach=True,
        environment={
            "MEILI_ENV": "production",
            "MEILI_NO_ANALYTICS": "true",
            "MEILI_MASTER_KEY": testing_meili_config.master_key,
        },
        ports=[7700],
        # hostname="0.0.0.0",
        host_config=docker.create_host_config(
            port_bindings={7700: 7700}, publish_all_ports=True
        ),
    )
    docker.start(container=container["Id"])

    try:
        yield container
    finally:
        # remove container
        docker.kill(container["Id"])
        docker.remove_container(container["Id"])
