#!/usr/bin/env python3
"""Capture golden description fixtures from the live spatial stage.

Run this in PHASE 2, once build_overlap_from_intrid_sid works against BCGW. It is
the intended way to PRODUCE the golden fixtures (see docs/IMPLEMENTATION_PLAN.md,
"Phase 2 deliverable — PRODUCE THE GOLDEN FIXTURES"). Do NOT hand-author fixtures
for non-trivial cases: a golden fixture needs a REAL structured overlap, which only
the live spatial stage can produce. Hand-built overlaps encode a guess about the
overlap rather than what the stage computes.

What it does, per tenure id from Query_2_result.csv:
  1. run the ID-path overlay  -> a StructuredOverlap
  2. pair it with that tenure's validated LEGAL_DESC from Query_2_result.csv
  3. write a fixture JSON in the shape tests/test_engine_golden.py auto-discovers:
       intrid_sid            capture provenance
       captured_at           capture date (the fabric is time-varying)
       overlap               the StructuredOverlap dict
       source_description    the raw historical LEGAL_DESC, verbatim, immutable
       expected_description  the text the engine must produce — INITIALLY a copy
                             of source_description

IMPORTANT — the human confirmation is load-bearing, and it is a CURATION step:
  The project owner must CONFIRM each captured overlap against the real
  description at the Phase 2 checkpoint before the pair is promoted. At that
  point the owner MAY EDIT expected_description to current house style (expand
  abbreviations, fix ordering the corpus was inconsistent about) — byte-matching
  unedited historical text is NOT the success metric (docs/rules.md).
  source_description stays verbatim for reference. Note: a capture can also
  legitimately disagree with an OLD description because the fabric changed since
  it was written — that is a curation signal, not an engine bug.

  Workflow:
    - capture to a staging dir (tests/fixtures/descriptions/_staging/)
    - inspect each; curate expected_description; move CONFIRMED ones to CORE
      (tests/fixtures/descriptions/core/) and harder ones to STRETCH
      (tests/fixtures/descriptions/stretch/), which may xfail.
  Only CORE fixtures are the must-pass regression basis.

The overlay call is the only stubbed spot; everything else here works now.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STAGING_DIR = REPO_ROOT / "tests" / "fixtures" / "descriptions" / "_staging"
QUERY2_DEFAULT = REPO_ROOT / "tests" / "fixtures" / "discovery" / "Query_2_result.csv"


def run_overlay(intrid_sid: str):
    """Produce the StructuredOverlap for one tenure. Phase 2 wires this."""
    # Phase 2:
    # from lds.spatial.overlay import build_overlap_from_intrid_sid
    # return build_overlap_from_intrid_sid(intrid_sid)
    raise NotImplementedError(
        "Phase 2: call build_overlap_from_intrid_sid(intrid_sid) here"
    )


def load_query2(csv_path: Path) -> dict[str, dict]:
    """Return {INTRID_SID: {"legal_desc": ..., "area_ha": ...}} from Query_2_result.csv."""
    rows: dict[str, dict] = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows[str(row["INTRID_SID"]).strip()] = {
                "legal_desc": row["LEGAL_DESC"],
                "area_ha": row.get("AREA_HA"),
            }
    return rows


def capture_one(intrid_sid: str, source_description: str, out_dir: Path) -> Path:
    """Run the overlay for one tenure and write a staged fixture JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)

    overlap = run_overlay(intrid_sid)
    fixture = {
        "intrid_sid": intrid_sid,
        "captured_at": datetime.date.today().isoformat(),
        "overlap": overlap.model_dump(mode="json"),
        "source_description": source_description,
        # starts as a copy; the owner curates it to house style at confirmation
        "expected_description": source_description,
    }

    out_path = out_dir / f"tenure_{intrid_sid}.json"
    out_path.write_text(
        json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "query2_csv",
        type=Path,
        nargs="?",
        default=QUERY2_DEFAULT,
        help="path to Query_2_result.csv (default: the committed discovery copy)",
    )
    parser.add_argument(
        "--ids",
        nargs="*",
        help="specific INTRID_SIDs to capture; default is a curated subset you define",
    )
    parser.add_argument(
        "--out", type=Path, default=STAGING_DIR, help="staging output directory"
    )
    args = parser.parse_args(argv)

    query2 = load_query2(args.query2_csv)
    ids = args.ids or []  # Phase 2: define a curated subset spanning the categories
    if not ids:
        print("Provide --ids (a curated subset spanning categories). See the plan.")
        return 1

    for intrid in ids:
        if intrid not in query2:
            print(f"  skip {intrid}: not in Query_2")
            continue
        path = capture_one(intrid, query2[intrid]["legal_desc"], args.out)
        print(f"  captured {intrid} -> {path}")

    print(
        "\nNow CONFIRM each staged overlap against its real description, curate "
        "expected_description to house style where needed, then move confirmed "
        "fixtures to descriptions/core/ (must-pass) or descriptions/stretch/ (xfail)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
