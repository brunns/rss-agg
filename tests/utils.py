from typing import TypeVar

T = TypeVar("T")


async def async_value[T](value: T) -> T:
    return value
