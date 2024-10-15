from typing import Any, AsyncGenerator

from examples.user.models import (
    User,
    UserPredicate,
    UserProfile,
    UserProfilePredicate,
    UserProfileUpdate,
    UserUpdate,
)
from examples.user.sqlite.context import SQLiteTransaction
from examples.user.storage import UserProfileStorage, UserStorage


class SQLiteUserProfileStorage(UserProfileStorage):
    def __init__(self, transaction: SQLiteTransaction):
        self.transaction = transaction

    async def get(
        self, where: UserProfilePredicate | None = None
    ) -> AsyncGenerator[UserProfile, Any]:
        query = "SELECT * FROM users_profile"
        params = []
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        async with self.transaction.tx_obj.execute(query, params) as cursor:
            async for row in cursor:
                yield UserProfile(
                    **dict(zip([column[0] for column in cursor.description], row))
                )
            await cursor.close()

    async def create(self, entities: list[UserProfile]) -> list[UserProfile]:
        for user_profile in entities:
            cursor = await self.transaction.tx_obj.execute(
                """
                INSERT INTO users_profile (username, first_name, last_name, user_id)
                VALUES (?, ?, ?, ?)
            """,
                (
                    user_profile.username,
                    user_profile.first_name,
                    user_profile.last_name,
                    user_profile.user_id,
                ),
            )
            user_profile.id = cursor.lastrowid
            await cursor.close()
        return entities

    async def delete(self, where: UserProfilePredicate) -> int:
        query = "DELETE FROM users_profile WHERE "
        conditions = []
        params = []
        for key, value in where.items():
            conditions.append(f"{key} = ?")
            params.append(value)
        query += " AND ".join(conditions)

        cursor = await self.transaction.tx_obj.execute(query, params)
        await cursor.close()
        return cursor.rowcount

    async def update(
        self, where: UserProfilePredicate, set_to: UserProfileUpdate
    ) -> int:
        set_query = ", ".join([f"{key} = ?" for key in set_to.keys()])
        where_query = " AND ".join([f"{key} = ?" for key in where.keys()])
        query = f"UPDATE users_profile SET {set_query} WHERE {where_query}"
        params = list(set_to.values()) + list(where.values())

        cursor = await self.transaction.tx_obj.execute(query, params)
        await cursor.close()
        return cursor.rowcount


class SQLiteUserStorage(UserStorage):
    def __init__(self, transaction: SQLiteTransaction):
        self.transaction = transaction

    async def get(
        self, where: UserPredicate | None = None
    ) -> AsyncGenerator[User, Any]:
        query = "SELECT * FROM users"
        params = []
        if where:
            conditions = []
            for key, value in where.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        async with self.transaction.tx_obj.execute(query, params) as cursor:
            async for row in cursor:
                yield User(
                    **dict(zip([column[0] for column in cursor.description], row))
                )
            await cursor.close()

    async def create(self, entities: list[User]) -> list[User]:
        for user in entities:
            cursor = await self.transaction.tx_obj.execute(
                """
                INSERT INTO users (email, is_active)
                VALUES (?, ?)
            """,
                (user.email, user.is_active),
            )
            user.id = cursor.lastrowid
            await cursor.close()
        return entities

    async def delete(self, where: UserPredicate) -> int:
        query = "DELETE FROM users WHERE "
        conditions = []
        params = []
        for key, value in where.items():
            conditions.append(f"{key} = ?")
            params.append(value)
        query += " AND ".join(conditions)

        cursor = await self.transaction.tx_obj.execute(query, params)
        await cursor.close()
        return cursor.rowcount

    async def update(self, where: UserPredicate, set_to: UserUpdate) -> int:
        set_query = ", ".join([f"{key} = ?" for key in set_to.keys()])
        where_query = " AND ".join([f"{key} = ?" for key in where.keys()])
        query = f"UPDATE users SET {set_query} WHERE {where_query}"
        params = list(set_to.values()) + list(where.values())

        cursor = await self.transaction.tx_obj.execute(query, params)
        await cursor.close()
        return cursor.rowcount
