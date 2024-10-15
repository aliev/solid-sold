import abc
import sys
from typing import TYPE_CHECKING, Any, AsyncGenerator, Generic, TypeVar, get_args

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:  # pragma: nocover
    from typing_extensions import Self


EntityType = TypeVar("EntityType")
UpdateType = TypeVar("UpdateType")
PredicateType = TypeVar("PredicateType")


class AbstractStorage(abc.ABC, Generic[EntityType, UpdateType, PredicateType]):
    @property
    def entity(self) -> EntityType:
        """Returns the entity class.

        This magic was done by extracting the class from type annotation.

        The `__orig_class__` contains the class with annotation:

            >> MyStorage[MyEntity]().__orig_class__
            => MyStorage[MyEntity]

        The `__orig_bases__` contains the tuple of base classes,
        because Python supports multiple inheritance:

            >> class MyStorage(AbstractBaseStorage[MyEntity]): ...
            >> MyStorage(AbstractBaseStorage[MyEntity]).__orig_class__
            => (MyStorage[MyEntity],)
        """
        self_cls: Self | None = None

        origin_class: Self | None = getattr(self, "__orig_class__", None)
        origin_bases: tuple[Self] | None = getattr(self, "__orig_bases__", None)

        if origin_class is not None:
            self_cls = origin_class
        elif origin_bases is not None:
            self_cls = origin_bases[0]
        else:
            RuntimeError("I was not able to find the entity model.")

        # Extracts the entity class.
        entity_cls, *_ = get_args(self_cls)

        return entity_cls

    @abc.abstractmethod
    async def get(
        self,
        where: PredicateType | None = None,
    ) -> AsyncGenerator[EntityType, Any]:
        """Retrieves entities by predicate.

        Args:
            where (PredicateType | None, optional): The predicate to filter entities. Defaults to None.
            tx_ctx (ContextType | None, optional): The transaction context. Defaults to None.

        Returns:
            AsyncGenerator[EntityType, Any]: An asynchronous generator yielding entities.

        Yields:
            EntityType: The next entity matching the predicate.
        """

        if TYPE_CHECKING:
            yield self.entity

    @abc.abstractmethod
    async def create(
        self,
        entities: list[EntityType],
    ) -> list[EntityType]:
        """Creates entities.

        Args:
            entities (list[EntityType]): The list of entities to create.
            tx_ctx (ContextType | None, optional): The transaction context. Defaults to None.

        Returns:
            list[EntityType]: The list of created entities.
        """

    @abc.abstractmethod
    async def delete(
        self,
        where: PredicateType,
    ) -> int:
        """Deletes entities by predicate.

        Args:
            where (PredicateType): The predicate to filter entities for deletion.
            tx_ctx (ContextType | None, optional): The transaction context. Defaults to None.

        Returns:
            int: The number of entities deleted.
        """

    @abc.abstractmethod
    async def update(
        self,
        where: PredicateType,
        set_to: UpdateType,
    ) -> int:
        """Updates entities by predicate.

        Args:
            where (PredicateType): The predicate to filter entities for updating.
            set_to (UpdateType): The values to update the entities with.
            tx_ctx (ContextType | None, optional): The transaction context. Defaults to None.

        Returns:
            int: The number of entities updated.
        """
