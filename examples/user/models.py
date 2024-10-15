from dataclasses import dataclass
from typing import NotRequired, TypedDict


@dataclass
class User:
    email: str
    id: int | None = None
    is_active: bool = False


class UserUpdate(TypedDict):
    id: NotRequired[int]
    username: NotRequired[str]
    email: NotRequired[str]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    is_active: NotRequired[bool]


class UserPredicate(TypedDict):
    id: NotRequired[int]
    username: NotRequired[str]
    email: NotRequired[str]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    is_active: NotRequired[bool]


@dataclass
class UserProfile:
    username: str
    first_name: str
    last_name: str
    id: int | None = None
    user_id: int | None = None


class UserProfileUpdate(TypedDict):
    username: NotRequired[str]
    first_name: NotRequired[str]
    last_name: NotRequired[str]


class UserProfilePredicate(TypedDict):
    username: NotRequired[str]
    first_name: NotRequired[str]
    last_name: NotRequired[str]
    id: NotRequired[int]
    user_id: NotRequired[int]
