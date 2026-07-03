"""Authoritative land-district gazetteer for output validation.

The vocabulary originates in the BCGW districts view (TA_LAND_DISTRICTS_SVW) —
NOT scraped from description text — but the engine is pure and must never touch
Oracle. So the vocabulary is a COMMITTED SNAPSHOT. The current snapshot was
seeded from the discovery extract (Query_3a, pulled 2026-06-18, 61 districts);
tools/export_land_districts.py refreshes it from the live view.

Used by engine/validate.py to check district names in the output and catch
typos / non-standard spellings. NOTE: the fabric stores names in UPPERCASE
("ALBERNI DISTRICT") while rendered descriptions use title case — the validator
must compare case-insensitively (or normalize both sides), not byte-equal.
"""

from __future__ import annotations

import json
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).parent / "data" / "land_districts.json"


def load_land_districts() -> set[str]:
    """Return the set of authoritative land-district names from the snapshot.

    Raises:
        FileNotFoundError: the snapshot has not been produced yet — run
            tools/export_land_districts.py against BCGW and commit the output.
    """
    if not SNAPSHOT_PATH.exists():
        raise FileNotFoundError(
            f"Land-district snapshot missing at {SNAPSHOT_PATH}. "
            "Run tools/export_land_districts.py (needs BCGW credentials) and "
            "commit the JSON it writes."
        )
    with open(SNAPSHOT_PATH, encoding="utf-8") as fh:
        snapshot = json.load(fh)
    return set(snapshot["districts"])
