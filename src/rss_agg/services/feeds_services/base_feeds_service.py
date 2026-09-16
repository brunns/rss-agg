# Copyright 2024-2026 Simon Brunning
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rss_agg.domain import domain


class FeedsService(ABC):
    @abstractmethod
    def get_feeds_and_exclusions(self) -> domain.FeedsAndExclusions: ...
