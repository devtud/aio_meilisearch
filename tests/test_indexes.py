import asyncio
from typing import List

import httpx
import pytest

from aio_meilisearch import indexes
from aio_meilisearch.common import MeiliConfig
from aio_meilisearch.types import IndexDict


def test_flow(loop: asyncio.AbstractEventLoop, testing_meili_config: MeiliConfig):
    response = loop.run_until_complete(indexes.get_all(testing_meili_config))

    assert len(response) == 0

    response = loop.run_until_complete(
        indexes.get_one(meili_config=testing_meili_config, name="books")
    )

    assert response is None

    with pytest.raises(httpx.HTTPStatusError) as e:
        _ = loop.run_until_complete(
            indexes.get_one(
                meili_config=testing_meili_config, name="books", raise_404=True
            )
        )

    assert e.value.response.status_code == httpx.codes.NOT_FOUND

    index: IndexDict = loop.run_until_complete(
        indexes.create_one(meili_config=testing_meili_config, name="books")
    )

    assert index["uid"] == "books"
    # assert index["primaryKey"] == "id"

    index_list: List[IndexDict] = loop.run_until_complete(
        indexes.get_all(meili_config=testing_meili_config)
    )

    assert len(index_list) == 1

    index: IndexDict = loop.run_until_complete(
        indexes.get_one(meili_config=testing_meili_config, name="books")
    )

    assert index["uid"] == "books"

    index: IndexDict = loop.run_until_complete(
        indexes.update_one(meili_config=testing_meili_config, name="books", pk="id")
    )

    assert index["primaryKey"] == "id"

    loop.run_until_complete(
        indexes.delete_one(meili_config=testing_meili_config, name="books")
    )

    index_list = loop.run_until_complete(
        indexes.get_all(meili_config=testing_meili_config)
    )

    assert len(index_list) == 0
