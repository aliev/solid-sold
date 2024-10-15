import aiosqlite

from solid_sold.context import AbstractTransactionalContext


class SQLiteTransaction(AbstractTransactionalContext[aiosqlite.Connection]):
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def close(self) -> None:
        await self.tx_obj.close()

    async def commit(self) -> None:
        """Commit transaction"""
        await self.tx_obj.commit()
        await self.close()

    async def rollback(self) -> None:
        """Rollback transaction"""
        await self.tx_obj.rollback()
        await self.close()

    async def start_transaction(self) -> aiosqlite.Connection:
        """Start transaction"""
        conn = await aiosqlite.connect(self.db_path)
        await conn.execute("BEGIN")
        return conn
