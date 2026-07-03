#!/usr/bin/env python3
"""Export the authoritative land-district vocabulary from BCGW to a committed
snapshot.

The text engine validates district names against this vocabulary but is pure
Python and never queries Oracle — so the vocabulary ships as a JSON snapshot
inside the engine package. Run this once in Phase 2 (and again if the view ever
changes), review the output, and commit it:

    BCGW_USER=... BCGW_PASSWORD=... BCGW_DSN=... uv run python tools/export_land_districts.py

Writes src/lds/engine/reference/data/land_districts.json with the district names
and the extract date.
"""

from __future__ import annotations

import datetime
import json
import os
import sys
from pathlib import Path

import oracledb

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "src" / "lds" / "engine" / "reference" / "data" / "land_districts.json"

VIEW = "WHSE_TANTALIS.TA_LAND_DISTRICTS_SVW"
NAME_COL = "LAND_DISTRICT_NAME"  # VERIFY against the view before first run


def main() -> int:
    user = os.getenv("BCGW_USER")
    password = os.getenv("BCGW_PASSWORD")
    dsn = os.getenv("BCGW_DSN")
    if not (user and password and dsn):
        print("Set BCGW_USER, BCGW_PASSWORD and BCGW_DSN in the environment.")
        return 2

    with oracledb.connect(user=user, password=password, dsn=dsn) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT {NAME_COL} FROM {VIEW} ORDER BY {NAME_COL}")
        districts = [row[0] for row in cursor.fetchall() if row[0]]

    if not districts:
        print("Query returned no district names — check the view/column names.")
        return 1

    snapshot = {
        "source_view": VIEW,
        "extracted_at": datetime.date.today().isoformat(),
        "districts": districts,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(districts)} districts to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
