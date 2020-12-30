from dataclasses import dataclass
from typing import TypedDict, Optional, Generic, TypeVar, List

T = TypeVar("T")


class IndexDict(TypedDict):
    uid: str
    primaryKey: Optional[str]
    createdAt: str
    updatedAt: str


class UpdateDict(TypedDict):
    status: str
    updateId: str
    type: dict
    duration: float
    enqueuedAt: str
    processedAt: str


@dataclass
class SearchResponse(Generic[T]):
    hits: List[T]
    offset: int
    limit: int
    nbHits: int
    exhaustiveNbHits: bool
    facetDistribution: dict
    exhaustiveFacetsCount: bool
    processingTimeMs: int
    query: str
