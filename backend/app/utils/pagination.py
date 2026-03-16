import math

"""Pagination utility for endpoints. From the sqlalchemy queries, a paginated result will return.
note: page_size is maximum was set previously. Method returns dictionary that contains restaurants for
requested page, plus num of results, curr. page number, and total num of pages.
"""
def paginate(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "total_pages": total_pages,
    }