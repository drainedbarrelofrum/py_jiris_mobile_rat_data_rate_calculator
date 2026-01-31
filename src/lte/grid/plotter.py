from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch

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

    def plot_combined(self, style: PlotStyle | None = None) -> None:
        mask = self._grid.combined_mask()
        style = style or PlotStyle(title="Combined Allocation")
        self.plot_mask(mask, style=style)

    def plot_allocation_map(
        self,
        channel_order: Iterable[str],
        style: PlotStyle | None = None,
        colors: Mapping[str, str] | None = None,
    ) -> None:
        style = style or PlotStyle(title="Allocation Map")
        colors = colors or {}

        sc, sym = self._grid.shape()
        alloc = [[0 for _ in range(sym)] for _ in range(sc)]

        channel_names = list(channel_order)
        for idx, name in enumerate(channel_names, start=1):
            mask = self._grid.get_mask(name)
            for i in range(sc):
                row = alloc[i]
                mrow = mask[i]
                for j in range(sym):
                    if mrow[j]:
                        row[j] = idx

        color_list = ["white"] + [
            colors.get(name, "tab:blue") for name in channel_names
        ]
        cmap = ListedColormap(color_list)
        norm = BoundaryNorm(list(range(len(color_list) + 1)), cmap.N)

        fig, ax = plt.subplots(figsize=style.figsize)
        ax.imshow(
            alloc,
            aspect="auto",
            origin="lower",
            cmap=cmap,
            norm=norm,
            interpolation="nearest",
        )
        if style.title:
            ax.set_title(style.title)
        ax.set_xlabel("Symbol Index")
        ax.set_ylabel("Subcarrier Index")
        if style.show_grid:
            ax.set_xticks(range(0, sym + 1), minor=True)
            ax.set_yticks(range(0, sc + 1), minor=True)
            ax.grid(which="minor", linewidth=0.2, alpha=0.3)
            ax.tick_params(which="minor", bottom=False, left=False)

        legend_items = [Patch(facecolor="white", edgecolor="black", label="Available")]
        for name in channel_names:
            legend_items.append(
                Patch(facecolor=colors.get(name, "tab:blue"), label=name)
            )
        ax.legend(handles=legend_items, loc="upper right", framealpha=0.9)

        plt.tight_layout()
        if style.save_path:
            path = Path(style.save_path)
            fig.savefig(path, format=style.format)
        if style.show:
            plt.show()
        plt.close(fig)
