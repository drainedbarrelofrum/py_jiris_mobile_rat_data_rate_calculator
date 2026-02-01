from __future__ import annotations

from abc import ABC, abstractmethod

from src.lte.grid.resource_grid import ResourceGrid


class Channel(ABC):
    name: str
    priority: int = 100

    @abstractmethod
    def allocate(self, grid: ResourceGrid) -> list[list[bool]]:
        raise NotImplementedError
