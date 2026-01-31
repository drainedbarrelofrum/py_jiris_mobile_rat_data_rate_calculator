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
    parser.add_argument(
        "--save-allocated-csv",
        action="store_true",
        help="Save allocation labels to data_output/grid_allocated.csv",
    )
    parser.add_argument(
        "--no-pbch",
        action="store_true",
        help="Disable PBCH allocation",
    )
    parser.add_argument(
        "--plot-combined",
        action="store_true",
        help="Plot combined allocation mask (includes PBCH if enabled)",
    )
    parser.add_argument(
        "--plot-allocation",
        default=None,
        help="Comma-separated channel list for allocation map (e.g., PBCH,PDCCH)",
    )
    parser.add_argument(
        "--allocation-colors",
        default=None,
        help="Comma-separated name=color pairs (e.g., PBCH=tab:orange,PDCCH=tab:blue)",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    channels = ("PBCH",)
    if args.plot_allocation:
        channels = tuple(c.strip() for c in args.plot_allocation.split(",") if c.strip())
    colors = None
    if args.allocation_colors:
        colors = {}
        for pair in args.allocation_colors.split(","):
            if "=" not in pair:
                continue
            name, color = pair.split("=", 1)
            name = name.strip()
            color = color.strip()
            if name:
                colors[name] = color
    runner = LteDlRunner.from_json(args.config)
    runner.run(
        RunOptions(
            plot_available=not args.no_plot,
            save_svg_path=args.save_svg,
            show_plot=not args.no_show,
            save_csv=args.save_csv,
            save_allocated_csv=args.save_allocated_csv,
            allocate_pbch=not args.no_pbch,
            plot_combined=args.plot_combined,
            plot_allocation_map=bool(args.plot_allocation),
            allocation_channels=channels,
            allocation_colors=colors,
        )
    )


if __name__ == "__main__":
    main()
