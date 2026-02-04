from typing import TypeVar

T = TypeVar("T")


async def future_returning[T](value: T) -> T:
    return value
