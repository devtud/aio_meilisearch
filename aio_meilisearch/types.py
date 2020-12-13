from typing import TypedDict, Optional


class IndexDict(TypedDict):
    uid: str
    primaryKey: Optional[str]
    createdAt: str
    updatedAt: str
