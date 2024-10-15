import asyncio
from typing import TYPE_CHECKING

import aiosqlite

from examples.user.services import EmailService, UserService
from examples.user.sqlite.context import SQLiteTransaction
from examples.user.sqlite.storage import SQLiteUserProfileStorage, SQLiteUserStorage


class ConsoleEmailService(EmailService):
    async def send_mail(
        self, *, sender: str, recipients: list[str], subject: str, body: str
    ):
        print(
            f"sender={sender}, recipients={recipients}, subject={subject}, body={body}"
        )


async def initialize(db_path: str):
    conn = await aiosqlite.connect(db_path)
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT 0
        )
    """
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT NOT NULL UNIQUE,
            first_name TEXT,
            last_name TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
    """
    )
    await conn.commit()
    await conn.close()


async def main():
    db_path = "users.db"
    await initialize(db_path)

    # Prepare all dependencies.
    email_service = ConsoleEmailService()
    transaction = SQLiteTransaction(db_path)
    user_storage = SQLiteUserStorage(transaction=transaction)
    user_profile_storage = SQLiteUserProfileStorage(transaction=transaction)

    # Inject all dependencies to the user service
    user_service = UserService(
        user_storage=user_storage,
        user_profile_storage=user_profile_storage,
        transaction=transaction,
        email=email_service,
    )

    # Make the API call for the user registration
    user_profile = await user_service.register(
        {
            "email": "ali@aliev.me",
            "first_name": "Ali",
            "last_name": "Aliyev",
            "username": "aliev",
        }
    )

    print(f"The following user's profile has been created: {user_profile}")

    if TYPE_CHECKING:
        assert user_profile.user_id is not None

    user = await user_service.get_user_details(user_profile.user_id)
    print(f"Fetched the following user from the database: {user}")

    print(f"Activating user with id: '{user_profile.user_id}'")

    # Make the API call for the user's account activation.
    await user_service.activate(user_id=user_profile.user_id)

    async with transaction:
        user = await anext(
            user_storage.get({"id": user_profile.user_id, "is_active": True}), None
        )
        print(f"The following user has been activated: {user}")


if __name__ == "__main__":
    asyncio.run(main())
