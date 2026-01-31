from src.lte.config.dimensions import grid_dimensions_from_config
from src.lte.grid.resource_grid import ResourceGrid


def test_resource_grid_shape_from_config() -> None:
    cfg = {
        "bw": 20,
        "cpType": "normal",
        "numSlotsPerSubframe": 2,
        "numSubframesPerFrame": 10,
        "subcarriersPerRb": 12,
    }
    dims = grid_dimensions_from_config(cfg)
    grid = ResourceGrid(dims)

    subcarriers, symbols = grid.shape()
    assert subcarriers == 1200
    assert symbols == 140


def test_resource_grid_shape_duration_ms() -> None:
    cfg = {
        "bw": 10,
        "cpType": "normal",
        "durationMs": 1000,
    }
    dims = grid_dimensions_from_config(cfg)
    grid = ResourceGrid(dims)
    subcarriers, symbols = grid.shape()
    assert subcarriers == 600
    assert symbols == 14000


def test_register_mask_shape_validation() -> None:
    cfg = {"bw": 5, "cpType": "normal"}
    dims = grid_dimensions_from_config(cfg)
    grid = ResourceGrid(dims)

    mask = grid.empty_mask()
    grid.register_mask("PDCCH", mask)

    bad_mask = [[False] * (grid.shape()[1] - 1) for _ in range(grid.shape()[0])]
    try:
        grid.register_mask("BAD", bad_mask)
        assert False, "Expected ValueError for bad mask shape"
    except ValueError:
        assert True
