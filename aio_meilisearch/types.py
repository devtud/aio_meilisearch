from typing import TypedDict, Optional, TypeVar, List, Protocol, overload, Literal

T = TypeVar("T")


class IndexDict(TypedDict):
    uid: str
    primaryKey: Optional[str]
    createdAt: str
    updatedAt: str


class IndexSettingsDict(TypedDict):
    synonyms: dict
    stopWords: List[str]
    rankingRules: List[str]
    attributesForFaceting: List[str]
    distinctAttribute: Optional[str]
    searchableAttributes: List[str]
    displayedAttributes: List[str]


class UpdateDict(TypedDict):
    status: str
    updateId: str
    type: dict
    duration: float
    enqueuedAt: str
    processedAt: str


class SearchResponse(Protocol[T]):
    @overload
    def __getitem__(self, item: Literal["hits"]) -> List[T]:
        ...

    @overload
    def __getitem__(self, item: Literal["offset"]) -> int:
        ...

    @overload
    def __getitem__(self, item: Literal["limit"]) -> int:
        ...

    @overload
    def __getitem__(self, item: Literal["nbHits"]) -> int:
        ...

    @overload
    def __getitem__(self, item: Literal["exhaustiveNbHits"]) -> bool:
        ...

    @overload
    def __getitem__(self, item: Literal["facetDistribution"]) -> dict:
        ...

    @overload
    def __getitem__(self, item: Literal["exhaustiveFacetsCount"]) -> bool:
        ...

    @overload
    def __getitem__(self, item: Literal["processingTimeMs"]) -> int:
        ...

    @overload
    def __getitem__(self, item: Literal["query"]) -> str:
        ...

    def __getitem__(self, item):
        return super().__getitem__(item)
