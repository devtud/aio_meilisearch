import json
from unittest import TestCase

import httpx

from aio_meilisearch.common import MeiliConfig, request
from tests.utils import DockerTestCase


class TestMeiliConfig(TestCase):
    def test_meili_config(self):
        meili_conf = MeiliConfig(
            base_url="http://someurl/",
            public_key="somekey",
        )

        self.assertEqual("http://someurl", meili_conf.base_url)


class TestMeiliRequest(DockerTestCase):
    async def test_request_keys_ok(self):
        async with httpx.AsyncClient() as http_client:
            response = await request(
                meili_config=self.meili_config,
                http_client=http_client,
                method="GET",
                endpoint="/keys",
                api_key=self.meili_config.master_key,
            )

        js = json.loads(response)

        assert js["private"] == self.meili_config.private_key
        assert js["public"] == self.meili_config.public_key

    async def test_request_keys_not_ok(self):
        with self.assertRaises(httpx.HTTPStatusError) as ctx:
            async with httpx.AsyncClient() as http_client:
                _ = await request(
                    meili_config=self.meili_config,
                    http_client=http_client,
                    method="GET",
                    endpoint="/keys",
                    api_key=self.meili_config.private_key,
                )
        assert ctx.exception.response.status_code == httpx.codes.FORBIDDEN
