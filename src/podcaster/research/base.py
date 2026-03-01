"""Abstract base class for all research modules."""

from __future__ import annotations

from abc import ABC, abstractmethod

from podcaster.config import Settings
from podcaster.models import PersonInput, ResearchItem


class BaseResearcher(ABC):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name of the research source."""

    @abstractmethod
    def is_available(self) -> bool:
        """Whether this researcher has the necessary config to run."""

    @abstractmethod
    async def research(self, person: PersonInput) -> list[ResearchItem]:
        """Gather research items for the given person."""
