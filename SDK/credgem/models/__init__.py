from typing import Any, List, NamedTuple


class PaginatedResponse(NamedTuple):
    data: List[Any]
    page: int
    page_size: int
    total_count: int
