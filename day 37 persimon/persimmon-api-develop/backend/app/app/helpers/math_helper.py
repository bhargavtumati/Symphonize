import math


def get_pagination(page: int, page_size: int, total_records: int):
    offset = (page - 1) * page_size
    total_pages = math.ceil(total_records / page_size)

    return {"offset": offset, "total_pages": total_pages}
