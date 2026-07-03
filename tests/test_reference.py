"""Engine reference data — real assertions, pass now."""

from __future__ import annotations

from lds.engine.reference.abbreviations import ABBREVIATIONS
from lds.engine.reference.land_districts import load_land_districts


def test_land_district_snapshot_loads():
    districts = load_land_districts()
    assert len(districts) > 50, "snapshot should carry the full district vocabulary"
    assert "ALBERNI DISTRICT" in districts
    # fabric names are uppercase; the validator compares case-insensitively
    assert all(d == d.upper() for d in districts)


def test_abbreviation_table_shape():
    assert ABBREVIATIONS["DL"] == "District Lot"
    # multi-word keys exist; the parser must attempt multi-word matches first
    assert "UNS PTNS" in ABBREVIATIONS
