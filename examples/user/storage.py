from examples.user.models import (
    User,
    UserPredicate,
    UserProfile,
    UserProfilePredicate,
    UserProfileUpdate,
    UserUpdate,
)
from solid_sold.base import AbstractStorage


class UserStorage(AbstractStorage[User, UserUpdate, UserPredicate]): ...


class UserProfileStorage(
    AbstractStorage[UserProfile, UserProfileUpdate, UserProfilePredicate]
): ...
