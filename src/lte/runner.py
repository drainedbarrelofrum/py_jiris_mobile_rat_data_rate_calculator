from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.lte.channels.pbch import PBCH, PBCHConfig
from src.lte.config.dimensions import grid_dimensions_from_config
from src.lte.grid.plotter import GridPlotter
from src.lte.grid.resource_grid import ResourceGrid


@dataclass(frozen=True)
class RunOptions:
    plot_available: bool = True
    save_svg_path: str | Path | None = None
    show_plot: bool = True
    save_csv: bool = False
    save_allocated_csv: bool = False
    allocate_pbch: bool = True
    plot_combined: bool = False
    plot_allocation_map: bool = False
    allocation_channels: tuple[str, ...] = ("PBCH",)
    allocation_colors: dict[str, str] | None = None


class LteDlRunner:
    """Top-level LTE DL runner: load config, build grid, plot, extend later."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        self._config = config
        self._grid: ResourceGrid | None = None

    @classmethod
    def from_json(cls, path: str | Path) -> "LteDlRunner":
        config_path = Path(path)
        with config_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls(data)

    @property
    def grid(self) -> ResourceGrid:
        if self._grid is None:
            dims = grid_dimensions_from_config(self._config)
            self._grid = ResourceGrid(dims)
        return self._grid

    def run(self, options: RunOptions | None = None) -> None:
        options = options or RunOptions()
        _ = self.grid
        if options.allocate_pbch:
            pbch = PBCH(PBCHConfig.from_config(self._config))
            self.grid.register_mask(pbch.name, pbch.allocate(self.grid))
        if options.save_csv:
            self.grid.export_available_csv_default()
        if options.save_allocated_csv:
            self.grid.export_allocation_csv_default(list(options.allocation_channels))
        if options.plot_available:
            plotter = GridPlotter(self.grid)
            plotter.plot_available(
                style=plotter_style(
                    save_path=options.save_svg_path, show=options.show_plot
                )
            )
        if options.plot_combined:
            plotter = GridPlotter(self.grid)
            plotter.plot_combined(
                style=plotter_style(
                    save_path=options.save_svg_path, show=options.show_plot
                )
            )
        if options.plot_allocation_map:
            plotter = GridPlotter(self.grid)
            plotter.plot_allocation_map(
                channel_order=options.allocation_channels,
                style=plotter_style(
                    save_path=options.save_svg_path, show=options.show_plot
                ),
                colors=options.allocation_colors,
            )


def plotter_style(save_path: str | Path | None, show: bool) -> "PlotStyle":
    from src.lte.grid.plotter import PlotStyle

    return PlotStyle(save_path=save_path, show=show, format="svg")
