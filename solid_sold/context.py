import abc
import logging
import sys
from contextvars import ContextVar
from typing import Generic, TypeVar
from uuid import uuid4

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:  # pragma: nocover
    from typing_extensions import Self

logger = logging.getLogger(__name__)

# This TypeVar is set for the transaction object variable (tx_obj) which
# refers to the session/object of the transaction that is taking place
TransactionType = TypeVar("TransactionType")
current_tx_id: ContextVar[str | None] = ContextVar("current_tx_id", default=None)


class AbstractTransactionalContext(Generic[TransactionType]):
    """
    Abstract base class for defining asynchronous transaction contexts with context preservation.
    """

    tx_objs: dict[str, TransactionType] = dict()

    @property
    def tx_obj(self) -> TransactionType:
        tx_id = current_tx_id.get()
        if tx_id is None:
            raise ValueError("No active transaction")
        return self.tx_objs[tx_id]

    @property
    def in_atomic_block(self) -> bool:
        tx_id = current_tx_id.get()
        return bool(tx_id)

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit transaction"""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction"""

    @abc.abstractmethod
    async def start_transaction(self) -> TransactionType:
        """Start transaction"""

    async def __aenter__(self) -> Self:
        """Entering the context causes a new database transaction to be created."""
        if current_tx_id.get() is None:
            new_tx_id = str(uuid4())
            current_tx_id.set(new_tx_id)
            self.tx_objs[new_tx_id] = await self.start_transaction()
        else:
            raise RuntimeError(
                "A durable transaction block cannot be nested within another "
                "transaction block."
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        tx_id = current_tx_id.get()

        try:
            if exc_type is None:
                try:
                    await self.commit()
                except Exception as commit_error:
                    logger.exception("Error occurred during transaction commit")
                    exc_val = commit_error
                    await self.rollback()
            else:
                await self.rollback()
        except Exception as error:
            logger.exception("Error occurred during transaction finalization")
            if exc_val is None:
                exc_val = error
        finally:
            if tx_id in self.tx_objs:
                del self.tx_objs[tx_id]
            current_tx_id.set(None)

        if exc_val is not None:
            raise exc_val
