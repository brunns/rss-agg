from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterable

    from rss_agg import domain


class FeedsAndExclusions(NamedTuple):
    feeds: Iterable[domain.FeedUrl]
    exclusions: Iterable[domain.ExcludeUrl]


class FeedsService(ABC):
    @abstractmethod
    def get_feeds_and_exclusions(self) -> FeedsAndExclusions: ...
