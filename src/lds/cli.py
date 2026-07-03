"""Batch CLI: tenure id(s) or geometry file(s) -> legal description(s).

Wires the spatial stage and the text engine together for headless/bulk use, and
can export the intermediate StructuredOverlap for inspection (the spreadsheet the
spatial stage validation gate reviews). Thin: all logic lives in the stages.

Subcommands land with their phases:
  overlap   ID|FILE  -> run spatial stage, export StructuredOverlap (Phase 2/3)
  describe  ID|FILE  -> full pipeline -> legal description (Phase 5)
"""

from __future__ import annotations

import argparse

from lds import __version__


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. `lds --help` and `lds --version` work from Phase 0."""
    parser = argparse.ArgumentParser(
        prog="lds",
        description="Legal Description Schedule generation for BC Crown land tenures.",
    )
    parser.add_argument("--version", action="version", version=f"lds {__version__}")

    subcommands = parser.add_subparsers(dest="command")

    overlap = subcommands.add_parser(
        "overlap",
        help="run the spatial stage and export the StructuredOverlap (Phase 2/3)",
    )
    overlap.add_argument("tenure", help="INTRID_SID or path to a geometry file")

    describe = subcommands.add_parser(
        "describe",
        help="run the full pipeline and print the legal description (Phase 5)",
    )
    describe.add_argument("tenure", help="INTRID_SID or path to a geometry file")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 2
    if args.command == "overlap":
        raise NotImplementedError("Phase 2: wire `overlap` to spatial.overlay")
    if args.command == "describe":
        raise NotImplementedError("Phase 5: wire `describe` to the full pipeline")
    return 2
