import abc
from typing import TypedDict

from examples.user.exceptions import UserDoesNotExist
from examples.user.models import User, UserProfile
from examples.user.storage import UserProfileStorage, UserStorage
from solid_sold.context import AbstractTransactionalContext


class UserData(TypedDict):
    username: str
    email: str
    first_name: str
    last_name: str


class EmailService(abc.ABC):
    @abc.abstractmethod
    async def send_mail(
        self,
        *,
        sender: str,
        recipients: list[str],
        subject: str,
        body: str,
    ): ...


class UserService:
    def __init__(
        self,
        user_storage: UserStorage,
        user_profile_storage: UserProfileStorage,
        email: EmailService,
        transaction: AbstractTransactionalContext,
    ) -> None:
        self.user_storage = user_storage
        self.user_profile_storage = user_profile_storage
        self.transaction = transaction
        self.email = email

    async def get_user_details(self, user_id: int) -> User:
        """Returns the user detail by it's id

        Args:
            user_id (int): user id.

        Returns:
            Profile: the profile object.
        """

        async with self.transaction:
            user = await anext(self.user_storage.get(where={"id": user_id}), None)

            if user is None:
                raise UserDoesNotExist(f"User with id '{user_id}' does not exist.")

            return user

    async def activate(self, user_id: int) -> None:
        """Activates user account by user_id

        Args:
            user_id (int): user id.

        Raises:
            UserDoesNotExist: If user with specific user_id does not exist.
        """
        async with self.transaction:
            user = await anext(
                self.user_storage.get(where={"id": user_id, "is_active": False}), None
            )

            if user is None:
                raise UserDoesNotExist(f"User with id '{user_id}' does not exist.")

            await self.user_storage.update(
                where={"id": user_id}, set_to={"is_active": True}
            )
            await self.email.send_mail(
                sender="noreply@xyz.com",
                recipients=[user.email],
                subject="Welcome to XYZ!",
                body="Your account has been verified!",
            )

    async def register(self, user_data: UserData) -> UserProfile:
        """Creates a user account.

        Args:
            user_data (UserData): user's data.
        """
        async with self.transaction:
            user = await self.user_storage.create([User(email=user_data["email"])])

            if len(user) < 1:
                raise

            user = user[0]

            user_profiles = await self.user_profile_storage.create(
                [
                    UserProfile(
                        username=user_data["username"],
                        first_name=user_data["first_name"],
                        last_name=user_data["last_name"],
                        user_id=user.id,
                    )
                ]
            )

            return user_profiles[0]
