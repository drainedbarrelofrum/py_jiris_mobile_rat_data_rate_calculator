from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class GridDimensions:
    num_rb: int
    num_subcarriers_per_rb: int
    num_symbols_per_slot: int
    num_slots_per_subframe: int
    num_subframes_per_frame: int
    num_frames: int = 1

    @property
    def num_subcarriers(self) -> int:
        return self.num_rb * self.num_subcarriers_per_rb

    @property
    def num_symbols_per_subframe(self) -> int:
        return self.num_symbols_per_slot * self.num_slots_per_subframe

    @property
    def num_symbols_per_frame(self) -> int:
        return self.num_symbols_per_subframe * self.num_subframes_per_frame

    @property
    def num_subframes_total(self) -> int:
        return self.num_subframes_per_frame * self.num_frames

    @property
    def num_symbols_total(self) -> int:
        return self.num_symbols_per_frame * self.num_frames


class ResourceGrid:
    """LTE DL time-frequency grid.

    Indices use (subcarrier, symbol) ordering for REs.
    The grid is a 2D matrix of shape [subcarrier][symbol].
    """

    def __init__(self, dims: GridDimensions) -> None:
        self._dims = dims
        self._masks: Dict[str, list[list[bool]]] = {}

    @property
    def dims(self) -> GridDimensions:
        return self._dims

    def shape(self) -> Tuple[int, int]:
        return (self._dims.num_subcarriers, self._dims.num_symbols_total)

    def subcarrier_index(self, rb: int, sc_in_rb: int) -> int:
        if rb < 0 or rb >= self._dims.num_rb:
            raise ValueError("rb out of range")
        if sc_in_rb < 0 or sc_in_rb >= self._dims.num_subcarriers_per_rb:
            raise ValueError("sc_in_rb out of range")
        return rb * self._dims.num_subcarriers_per_rb + sc_in_rb

    def rb_sc_from_subcarrier(self, subcarrier: int) -> Tuple[int, int]:
        if subcarrier < 0 or subcarrier >= self._dims.num_subcarriers:
            raise ValueError("subcarrier out of range")
        rb = subcarrier // self._dims.num_subcarriers_per_rb
        sc_in_rb = subcarrier % self._dims.num_subcarriers_per_rb
        return rb, sc_in_rb

    def symbol_index(self, subframe: int, slot: int, symbol: int) -> int:
        if subframe < 0 or subframe >= self._dims.num_subframes_total:
            raise ValueError("subframe out of range")
        if slot < 0 or slot >= self._dims.num_slots_per_subframe:
            raise ValueError("slot out of range")
        if symbol < 0 or symbol >= self._dims.num_symbols_per_slot:
            raise ValueError("symbol out of range")
        return subframe * self._dims.num_symbols_per_subframe + slot * self._dims.num_symbols_per_slot + symbol

    def symbol_index_from_frame(
        self, frame: int, subframe: int, slot: int, symbol: int
    ) -> int:
        if frame < 0 or frame >= self._dims.num_frames:
            raise ValueError("frame out of range")
        if subframe < 0 or subframe >= self._dims.num_subframes_per_frame:
            raise ValueError("subframe out of range")
        absolute_subframe = frame * self._dims.num_subframes_per_frame + subframe
        return self.symbol_index(
            subframe=absolute_subframe, slot=slot, symbol=symbol
        )

    def frame_subframe_slot_symbol_from_index(
        self, symbol_index: int
    ) -> Tuple[int, int, int, int]:
        if symbol_index < 0 or symbol_index >= self._dims.num_symbols_total:
            raise ValueError("symbol_index out of range")
        frame = symbol_index // self._dims.num_symbols_per_frame
        in_frame = symbol_index % self._dims.num_symbols_per_frame
        subframe = in_frame // self._dims.num_symbols_per_subframe
        in_subframe = in_frame % self._dims.num_symbols_per_subframe
        slot = in_subframe // self._dims.num_symbols_per_slot
        symbol = in_subframe % self._dims.num_symbols_per_slot
        return frame, subframe, slot, symbol

    def symbol_range_for_subframe(self, subframe: int) -> range:
        if subframe < 0 or subframe >= self._dims.num_subframes_total:
            raise ValueError("subframe out of range")
        start = subframe * self._dims.num_symbols_per_subframe
        end = start + self._dims.num_symbols_per_subframe
        return range(start, end)

    def symbol_range_for_frame(self, frame: int) -> range:
        if frame < 0 or frame >= self._dims.num_frames:
            raise ValueError("frame out of range")
        start = frame * self._dims.num_symbols_per_frame
        end = start + self._dims.num_symbols_per_frame
        return range(start, end)

    def symbol_range_for_slot(self, subframe: int, slot: int) -> range:
        start = self.symbol_index(subframe=subframe, slot=slot, symbol=0)
        end = start + self._dims.num_symbols_per_slot
        return range(start, end)

    def empty_mask(self) -> list[list[bool]]:
        sc, sym = self.shape()
        return [[False for _ in range(sym)] for _ in range(sc)]

    def register_mask(self, name: str, mask: list[list[bool]]) -> None:
        sc, sym = self.shape()
        if len(mask) != sc or any(len(row) != sym for row in mask):
            raise ValueError("Mask shape does not match grid shape")
        self._masks[name] = mask

    def get_mask(self, name: str) -> list[list[bool]]:
        return self._masks[name]

    def combined_mask(self) -> list[list[bool]]:
        sc, sym = self.shape()
        combined = self.empty_mask()
        for mask in self._masks.values():
            for i in range(sc):
                row = combined[i]
                mrow = mask[i]
                for j in range(sym):
                    row[j] = row[j] or mrow[j]
        return combined

    def available_mask(self) -> list[list[bool]]:
        sc, sym = self.shape()
        combined = self.combined_mask()
        available = self.empty_mask()
        for i in range(sc):
            for j in range(sym):
                available[i][j] = not combined[i][j]
        return available
