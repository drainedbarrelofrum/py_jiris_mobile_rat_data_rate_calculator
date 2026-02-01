from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class LteDlConfig:
    name: str = "LTE_DL_default"
    rat: str = "LTE"
    direction: str = "DL"
    transmission_duplex: str = "FDD"
    bw: int = 20
    cp_type: str = "normal"
    num_rb: int | None = None
    subcarriers_per_rb: int = 12
    num_slots_per_subframe: int = 2
    num_subframes_per_frame: int = 10
    duration_ms: int = 10
    dl_layers: int = 4
    ul_layers: int = 1
    dl_qm: int = 8
    ul_qm: int = 8
    cfi: int = 2
    cell_id: int = 0
    num_cell_ref_ports: int = 1
    gap_pattern: int = 0
    pucch_regions: int = 1
    prach_cfg_index: int = 0
    mbsfn_radio_frame_allocation_period: int = 10
    mbsfn_subframes: int = 1
    tdd_config: int = 0
    special_subframe_config: int = 0
    is_dss: int = 0
    oh_approximation: int = 0
    log_level: int = 0

    @classmethod
    def from_mapping(cls, cfg: Mapping[str, Any]) -> "LteDlConfig":
        data = {
            "name": cfg.get("name", cls.name),
            "rat": cfg.get("rat", cls.rat),
            "direction": cfg.get("direction", cls.direction),
            "transmission_duplex": cfg.get("transmissionDuplex", cls.transmission_duplex),
            "bw": int(cfg.get("bw", cls.bw)),
            "cp_type": cfg.get("cpType", cls.cp_type),
            "num_rb": cfg.get("numRb", cls.num_rb),
            "subcarriers_per_rb": int(cfg.get("subcarriersPerRb", cls.subcarriers_per_rb)),
            "num_slots_per_subframe": int(cfg.get("numSlotsPerSubframe", cls.num_slots_per_subframe)),
            "num_subframes_per_frame": int(cfg.get("numSubframesPerFrame", cls.num_subframes_per_frame)),
            "duration_ms": int(cfg.get("durationMs", cls.duration_ms)),
            "dl_layers": int(cfg.get("dlLayers", cls.dl_layers)),
            "ul_layers": int(cfg.get("ulLayers", cls.ul_layers)),
            "dl_qm": int(cfg.get("DL_Qm", cls.dl_qm)),
            "ul_qm": int(cfg.get("UL_Qm", cls.ul_qm)),
            "cfi": int(cfg.get("cfi", cls.cfi)),
            "cell_id": int(cfg.get("cellId", cls.cell_id)),
            "num_cell_ref_ports": int(cfg.get("numCellRefPorts", cls.num_cell_ref_ports)),
            "gap_pattern": int(cfg.get("gapPattern", cls.gap_pattern)),
            "pucch_regions": int(cfg.get("pucchRegions", cls.pucch_regions)),
            "prach_cfg_index": int(cfg.get("prachCfgIndex", cls.prach_cfg_index)),
            "mbsfn_radio_frame_allocation_period": int(
                cfg.get("MBSFNRadioFrameAllocationPeriod", cls.mbsfn_radio_frame_allocation_period)
            ),
            "mbsfn_subframes": int(cfg.get("MBSFNsubframes", cls.mbsfn_subframes)),
            "tdd_config": int(cfg.get("tddConfig", cls.tdd_config)),
            "special_subframe_config": int(
                cfg.get("specialSubframeConfig", cls.special_subframe_config)
            ),
            "is_dss": int(cfg.get("isDSS", cls.is_dss)),
            "oh_approximation": int(cfg.get("ohApproximation", cls.oh_approximation)),
            "log_level": int(cfg.get("logLevel", cls.log_level)),
        }
        return cls(**data)

    def validate(self) -> None:
        if self.rat != "LTE":
            raise ValueError("rat must be LTE")
        if self.direction != "DL":
            raise ValueError("direction must be DL")
        if self.transmission_duplex not in ("FDD", "TDD"):
            raise ValueError("transmissionDuplex must be FDD or TDD")
        if self.cp_type.lower() not in ("normal", "extended"):
            raise ValueError("cpType must be normal or extended")
        if self.duration_ms % 10 != 0:
            raise ValueError("durationMs must be a multiple of 10")
        if self.cell_id < 0 or self.cell_id > 503:
            raise ValueError("cellId must be in range 0..503")
        if self.num_cell_ref_ports not in (1, 2, 4):
            raise ValueError("numCellRefPorts must be 1, 2, or 4")
