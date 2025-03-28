from math import ceil
from typing import Any, Generic, TypeVar
from collections.abc import Sequence
from fastapi_pagination import Params, Page
from fastapi_pagination.bases import AbstractPage, AbstractParams
from pydantic import Field
from pydantic.generics import GenericModel

DataType = TypeVar("DataType")
T = TypeVar("T")


class PageBase(Page[T], Generic[T]):
    previous_page: int | None = Field(
        None, description="Page number of the previous page"
    )
    next_page: int | None = Field(None, description="Page number of the next page")


class ResponseBase(GenericModel, Generic[T]):
    message: str = ""
    meta: dict = {}
    data: T | None


class GetResponsePaginated(AbstractPage[T], Generic[T]):
    message: str | None = ""
    meta: dict = {}
    data: PageBase[T]

    __params_type__ = Params  # Set params related to Page

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
    ) -> PageBase[T] | None:
        if params.size is not None and total is not None and params.size != 0:
            pages = ceil(total / params.size)
        else:
            pages = 0

        return cls(
            data=PageBase[T](
                items=items,
                page=params.page,
                size=params.size,
                total=total,
                pages=pages,
                next_page=params.page + 1 if params.page < pages else None,
                previous_page=params.page - 1 if params.page > 1 else None,
            )
        )


class GetResponseBase(ResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data got correctly"


class PostResponseBase(ResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data created correctly"


class PutResponseBase(ResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data updated correctly"


class DeleteResponseBase(ResponseBase[DataType], Generic[DataType]):
    message: str | None = "Data deleted correctly"


def create_response(
    data: DataType,
    message: str | None = None,
    meta: dict | Any | None = {},
) -> (
    ResponseBase[DataType]
    | GetResponsePaginated[DataType]
    | GetResponseBase[DataType]
    | PutResponseBase[DataType]
    | DeleteResponseBase[DataType]
    | PostResponseBase[DataType]
):
    if isinstance(data, GetResponsePaginated):
        data.message = "Data paginated correctly" if message is None else message
        data.meta = meta
        return data
    if message is None:
        return {"data": data, "meta": meta}
    return {"data": data, "message": message, "meta": meta}
