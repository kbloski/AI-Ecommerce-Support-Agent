from dataclasses import dataclass, field
from collections.abc import Callable
from typing import Any, Generic, List, TypeVar

T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total_items: int
    total_pages: int = field(init=False)

    def __post_init__(self):
        if self.page_size <= 0:
            self.total_pages = 0
        else:
            self.total_pages = (
                self.total_items + self.page_size - 1
            ) // self.page_size

    def to_dict(self, serialize_item: Callable[[T], Any] | None = None) -> dict:
        serializer = serialize_item or (lambda item: item)
        return {
            "items": [serializer(item) for item in self.items],
            "page": self.page,
            "page_size": self.page_size,
            "total_items": self.total_items,
            "total_pages": self.total_pages,
        }
