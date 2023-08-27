from __future__ import annotations

from inspect import isawaitable
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from uuid import UUID

from litestar.controller.base import Controller
from litestar.repository.filters import CollectionFilter

if TYPE_CHECKING:
    from litestar import Request
    from litestar.repository import AbstractAsyncRepository, AbstractSyncRepository

ModelT = TypeVar("ModelT")
IdFieldT = TypeVar("IdFieldT", str, int, UUID)


class ItemIdsRequestBody(Generic[IdFieldT]):
    item_ids: list[IdFieldT]


class GenericController(Controller, Generic[ModelT, IdFieldT]):
    repository_type: type[AbstractAsyncRepository[ModelT]] | type[AbstractSyncRepository[ModelT]]
    id_field_type: IdFieldT
    id_field_name: str = "id"

    def create_repository(
        self, *, request: Request[Any, Any, Any], **kwargs: Any
    ) -> AbstractAsyncRepository[ModelT] | AbstractSyncRepository[ModelT]:
        kwargs["request"] = request
        return self.repository_type(**kwargs)

    async def create_instance(self, data: dict[str, Any], request: Request[Any, Any, Any]) -> ModelT:
        result = self.create_repository(request=request).add(data=data)
        return result if not isawaitable(result) else await result

    async def update_instance(self, data: dict[str, Any], item_id: IdFieldT, request: Request[Any, Any, Any]) -> ModelT:
        instance = self.create_repository(request=request).get(item_id=item_id)
        for k, v in data.items():
            setattr(instance, k, v)

        result = self.create_repository(request=request).update(data=instance)
        return result if not isawaitable(result) else await result

    async def delete_instance(self, item_id: IdFieldT, request: Request[Any, Any, Any]) -> None:
        result = self.create_repository(request=request).delete(item_id=item_id)
        if isawaitable(result):
            await result

    async def get_instance(self, item_id: IdFieldT, request: Request[Any, Any, Any]) -> ModelT:
        result = self.create_repository(request=request).get(item_id=item_id)
        return result if not isawaitable(result) else await result

    async def create_many(self, data: list[dict[str, Any]], request: Request[Any, Any, Any]) -> list[ModelT]:
        result = self.create_repository(request=request).add_many(data)
        return result if not isawaitable(result) else await result

    async def update_many(self, data: list[dict[str, Any]], request: Request[Any, Any, Any]) -> list[ModelT]:
        result = self.create_repository(request=request).update_many(data=data)
        return result if not isawaitable(result) else await result

    async def delete_many(self, data: ItemIdsRequestBody[IdFieldT], request: Request[Any, Any, Any]) -> None:
        result = self.create_repository(request=request).delete_many(item_ids=data.item_ids)
        if isawaitable(result):
            await result

    async def get_many(self, data: ItemIdsRequestBody[IdFieldT], request: Request[Any, Any, Any]) -> list[ModelT]:
        result = self.create_repository(request=request).list(
            CollectionFilter(field_name=self.id_field_name, values=[data.item_ids])
        )
        return result if not isawaitable(result) else await result
