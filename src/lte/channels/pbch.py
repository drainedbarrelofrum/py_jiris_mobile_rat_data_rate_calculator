from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Set, Tuple

from src.lte.channels.base import Channel
from src.lte.grid.resource_grid import ResourceGrid


@dataclass(frozen=True)
class PBCHConfig:
    cell_id: int
    cp_type: str
    transmission_duplex: str
    num_cell_ref_ports: int = 1

    @classmethod
    def from_config(cls, cfg: Mapping[str, Any]) -> "PBCHConfig":
        cell_id = int(cfg.get("cellId", 0))
        if cell_id < 0 or cell_id > 503:
            raise ValueError("cellId must be in range 0..503")

        cp_type = str(cfg.get("cpType", "normal")).lower()
        if cp_type not in ("normal", "extended"):
            raise ValueError("cpType must be 'normal' or 'extended'")

        duplex = str(cfg.get("transmissionDuplex", "FDD")).upper()
        if duplex not in ("FDD", "TDD"):
            raise ValueError("transmissionDuplex must be 'FDD' or 'TDD'")

        num_ports = int(cfg.get("numCellRefPorts", 1))
        if num_ports not in (1, 2, 4):
            raise ValueError("numCellRefPorts must be 1, 2, or 4")

        return cls(
            cell_id=cell_id,
            cp_type=cp_type,
            transmission_duplex=duplex,
            num_cell_ref_ports=num_ports,
        )


class PBCH(Channel):
    """PBCH mapping for LTE DL grid (TS 36.211)."""

    name = "PBCH"

    def __init__(self, config: PBCHConfig) -> None:
        self._config = config

    def allocate(self, grid: ResourceGrid) -> list[list[bool]]:
        mask = grid.empty_mask()
        dims = grid.dims

        if dims.num_symbols_per_slot < 4:
            raise ValueError("PBCH requires at least 4 symbols per slot")

        pbch_symbols = [0, 1, 2, 3]
        slot_in_subframe = 1
        subframe_in_frame = 0

        pbch_subcarriers = self._pbch_subcarrier_indices(dims.num_rb)
        crs_set = self._crs_positions(
            num_subcarriers=dims.num_subcarriers,
            cell_id=self._config.cell_id,
            cp_type=self._config.cp_type,
        )

        for frame in range(dims.num_frames):
            for l in pbch_symbols:
                symbol_index = grid.symbol_index_from_frame(
                    frame=frame,
                    subframe=subframe_in_frame,
                    slot=slot_in_subframe,
                    symbol=l,
                )
                for k in pbch_subcarriers:
                    if (k, l) in crs_set:
                        continue
                    mask[k][symbol_index] = True

        return mask

    @staticmethod
    def _pbch_subcarrier_indices(num_rb: int) -> range:
        center = (num_rb * 12) // 2
        start = center - 36
        end = center + 36
        return range(start, end)

    @staticmethod
    def _crs_positions(
        num_subcarriers: int, cell_id: int, cp_type: str
    ) -> Set[Tuple[int, int]]:
        v_shift = cell_id % 6
        if cp_type == "normal":
            symbol_sets = {
                0: (0, 4),  # ports 0/1
                1: (0, 4),
                2: (1,),  # ports 2/3
                3: (1,),
            }
        else:
            symbol_sets = {
                0: (0, 3),
                1: (0, 3),
                2: (1,),
                3: (1,),
            }

        crs: Set[Tuple[int, int]] = set()
        for port, symbols in symbol_sets.items():
            offset = 0 if port in (0, 2) else 3
            for l in symbols:
                for k in range(v_shift + offset, num_subcarriers, 6):
                    crs.add((k, l))
        return crs
