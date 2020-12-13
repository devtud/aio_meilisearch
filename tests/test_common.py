import asyncio
import json

import httpx
import pytest

from aio_meilisearch.common import MeiliConfig, request


def test_meili_config():
    meili_conf = MeiliConfig(
        http_client=httpx.AsyncClient(),
        base_url="http://someurl/",
        public_key="somekey",
    )

    assert meili_conf.base_url == "http://someurl"


def test_request_keys_ok(
    loop: asyncio.AbstractEventLoop, testing_meili_config: MeiliConfig
):
    response = loop.run_until_complete(
        request(
            meili_config=testing_meili_config,
            method="GET",
            endpoint="/keys",
            api_key=testing_meili_config.master_key,
        )
    )

    js = json.loads(response)

    assert js["private"] == testing_meili_config.private_key
    assert js["public"] == testing_meili_config.public_key


def test_request_keys_not_ok(
    loop: asyncio.AbstractEventLoop, testing_meili_config: MeiliConfig
):
    with pytest.raises(httpx.HTTPStatusError) as e:
        _ = loop.run_until_complete(
            request(
                meili_config=testing_meili_config,
                method="GET",
                endpoint="/keys",
                api_key=testing_meili_config.private_key,
            )
        )

    assert e.value.response.status_code == httpx.codes.FORBIDDEN
