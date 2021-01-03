[![Tests](https://github.com/devtud/aio_meilisearch/workflows/Tests/badge.svg)](https://github.com/devtud/aio_meilisearch/actions?workflow=Tests)
![pypi](https://img.shields.io/pypi/v/aio_meilisearch.svg)
![versions](https://img.shields.io/pypi/pyversions/aio_meilisearch.svg)
[![](https://pypip.in/license/aio_meilisearch/badge.svg)](https://pypi.python.org/pypi/aio_meilisearch)

# AIO_MEILISEARCH
## Async Wrapper over Meilisearch REST API with type hints

```bash
pip install aio_meilisearch
```

## Usage

```python
from typing import TypedDict, List, Optional
import httpx
from aio_meilisearch import (
    MeiliSearch,
    MeiliConfig,
    Index,
    SearchResponse,
)


class MovieDict(TypedDict):
    id: str
    name: str
    genres: List[str]
    url: str
    year: int


http = httpx.AsyncClient()

meilisearch = MeiliSearch(
    meili_config=MeiliConfig(
        base_url='http://localhost:7700',
        private_key='PRIVATE_KEY',
        public_key='PUBLIC_KEY',
    ),
    http_client=http,
)


index: Index[MovieDict] = await meilisearch.create_index(name="movies", pk="id")

await index.update_settings(
    {
        "searchableAttributes": ["name", "genres"],
        "displayedAttributes": [
            "name",
            "genres",
            "id",
            "url",
            "year",
        ],
        "attributesForFaceting": ["genres", "year"],
    }
)

movie_list: List[MovieDict] = [
    {
        "name": "Oblivion",
        "genres": ["action", "adventure", "sci-fi"],
        "id": "tt1483013",
        "url": "https://www.imdb.com/title/tt1483013/",
        "year": 2013,
    }
]

await index.documents.add_many(movie_list)

response: SearchResponse[MovieDict] = await index.documents.search(query="action")
```

## Contributing

**Prerequisites:**
 - **poetry**
 - **nox**
 - **nox-poetry**

Install them on your system:
```bash
pip install poetry nox nox-poetry
```

Run tests:
```bash
nox
```