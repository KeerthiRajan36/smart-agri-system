from math import ceil
from typing import Optional, Tuple, List, Any

from sqlalchemy.orm import Query


def paginate(
    query: Query,
    model,
    page: int = 1,
    limit: int = 10,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> Tuple[List[Any], int, int]:
    if sort_by and hasattr(model, sort_by):
        column = getattr(model, sort_by)
        query = query.order_by(column.desc() if sort_order == "desc" else column.asc())

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = ceil(total / limit) if limit else 1
    return items, total, total_pages
