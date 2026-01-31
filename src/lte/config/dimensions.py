from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.lte.grid.resource_grid import GridDimensions


@dataclass(frozen=True)
class LteDlGridConfig:
    bw_mhz: int
    cp_type: str
    num_slots_per_subframe: int = 2
    num_subframes_per_frame: int = 10
    num_subcarriers_per_rb: int = 12
    num_frames: int = 1


_BW_TO_RB = {
    1: 6,
    3: 15,
    5: 25,
    10: 50,
    15: 75,
    20: 100,
}


def _symbols_per_slot(cp_type: str) -> int:
    if cp_type.lower() == "normal":
        return 7
    if cp_type.lower() == "extended":
        return 6
    raise ValueError("cpType must be 'normal' or 'extended'")


def grid_dimensions_from_config(cfg: Mapping[str, Any]) -> GridDimensions:
    bw = int(cfg.get("bw", 20))
    if bw not in _BW_TO_RB:
        raise ValueError("bw must be one of 1, 3, 5, 10, 15, 20 MHz")

    cp_type = str(cfg.get("cpType", "normal"))
    num_symbols_per_slot = _symbols_per_slot(cp_type)

    num_rb = int(cfg.get("numRb", _BW_TO_RB[bw]))
    if num_rb != _BW_TO_RB[bw]:
        raise ValueError("numRb does not match bw for LTE")

    num_frames = int(cfg.get("numFrames", 1))
    duration_ms = cfg.get("durationMs", None)
    if duration_ms is not None:
        duration_ms = int(duration_ms)
        if duration_ms % 10 != 0:
            raise ValueError("durationMs must be a multiple of 10")
        num_frames = duration_ms // 10
    if num_frames < 1:
        raise ValueError("numFrames must be >= 1")

    return GridDimensions(
        num_rb=num_rb,
        num_subcarriers_per_rb=int(cfg.get("subcarriersPerRb", 12)),
        num_symbols_per_slot=num_symbols_per_slot,
        num_slots_per_subframe=int(cfg.get("numSlotsPerSubframe", 2)),
        num_subframes_per_frame=int(cfg.get("numSubframesPerFrame", 10)),
        num_frames=num_frames,
    )
