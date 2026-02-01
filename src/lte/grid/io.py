from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from src.lte.grid.resource_grid import ResourceGrid


@dataclass(frozen=True)
class GridIO:
    grid: ResourceGrid
    output_dir: Path = Path("data_output")

    def export_mask_csv(self, mask: list[list[bool]], path: str | Path) -> None:
        csv_path = Path(path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        sc_count, sym_count = self.grid.shape()
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            header = ["subcarrier_index"] + [f"sym_{i}" for i in range(sym_count)]
            writer.writerow(header)
            for sc_idx, row in enumerate(mask):
                if len(row) != sym_count:
                    raise ValueError("Mask row length does not match grid shape")
                writer.writerow([sc_idx] + [int(v) for v in row])

    def export_available_csv(self, path: str | Path | None = None) -> Path:
        path = Path(path) if path else self.output_dir / "grid_available.csv"
        self.export_mask_csv(self.grid.available_mask(), path)
        return path

    def export_allocation_csv(
        self, channel_order: Iterable[str], path: str | Path | None = None
    ) -> Path:
        sc_count, sym_count = self.grid.shape()
        alloc = [["Available" for _ in range(sym_count)] for _ in range(sc_count)]
        for name in channel_order:
            mask = self.grid.get_mask(name)
            for i in range(sc_count):
                row = alloc[i]
                mrow = mask[i]
                for j in range(sym_count):
                    if mrow[j]:
                        row[j] = name

        path = Path(path) if path else self.output_dir / "grid_allocated.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            header = ["subcarrier_index"] + [f"sym_{i}" for i in range(sym_count)]
            writer.writerow(header)
            for sc_idx, row in enumerate(alloc):
                writer.writerow([sc_idx] + row)
        return path
