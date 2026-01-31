from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib.pyplot as plt

from src.lte.grid.resource_grid import ResourceGrid


@dataclass(frozen=True)
class PlotStyle:
    figsize: tuple[int, int] = (12, 5)
    cmap: str = "Greys"
    show_grid: bool = True
    title: str | None = None
    show: bool = True
    save_path: str | Path | None = None
    format: str = "svg"


class GridPlotter:
    """Plot LTE DL resource grid occupancy masks."""

    def __init__(self, grid: ResourceGrid) -> None:
        self._grid = grid

    def plot_mask(self, mask: list[list[bool]], style: PlotStyle | None = None) -> None:
        style = style or PlotStyle()
        fig, ax = plt.subplots(figsize=style.figsize)
        ax.imshow(mask, aspect="auto", origin="lower", cmap=style.cmap, interpolation="nearest")
        if style.title:
            ax.set_title(style.title)
        ax.set_xlabel("Symbol Index")
        ax.set_ylabel("Subcarrier Index")
        if style.show_grid:
            ax.set_xticks(range(0, len(mask[0]) + 1), minor=True)
            ax.set_yticks(range(0, len(mask) + 1), minor=True)
            ax.grid(which="minor", linewidth=0.2, alpha=0.3)
            ax.tick_params(which="minor", bottom=False, left=False)
        plt.tight_layout()
        if style.save_path:
            path = Path(style.save_path)
            fig.savefig(path, format=style.format)
        if style.show:
            plt.show()
        plt.close(fig)

    def plot_channels(
        self,
        channels: Iterable[str],
        styles: Mapping[str, PlotStyle] | None = None,
    ) -> None:
        styles = styles or {}
        for name in channels:
            mask = self._grid.get_mask(name)
            style = styles.get(name, PlotStyle(title=name))
            self.plot_mask(mask, style=style)

    def plot_available(self, style: PlotStyle | None = None) -> None:
        mask = self._grid.available_mask()
        style = style or PlotStyle(title="Available REs")
        self.plot_mask(mask, style=style)
