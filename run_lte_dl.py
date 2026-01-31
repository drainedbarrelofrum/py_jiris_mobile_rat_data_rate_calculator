from __future__ import annotations

import argparse

from src.lte.runner import LteDlRunner, RunOptions


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LTE DL grid runner")
    parser.add_argument(
        "--config",
        default="config/lte_dl_default.json",
        help="Path to LTE DL config JSON",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Disable plotting of available REs",
    )
    parser.add_argument(
        "--save-svg",
        default=None,
        help="Save plot to SVG path (disables GUI if --no-show is used)",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Do not open a GUI window for plots",
    )
    parser.add_argument(
        "--save-csv",
        action="store_true",
        help="Save available grid mask to data_output/grid_available.csv",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    runner = LteDlRunner.from_json(args.config)
    runner.run(
        RunOptions(
            plot_available=not args.no_plot,
            save_svg_path=args.save_svg,
            show_plot=not args.no_show,
            save_csv=args.save_csv,
        )
    )


if __name__ == "__main__":
    main()
