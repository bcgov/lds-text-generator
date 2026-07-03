"""Abbreviation tables for parsing the registry's heavy abbreviations.

See docs/parsing_complexity.md for the forms (PCL., BLK., PL., RGES., SEC.S,
UNS PTNS, DIST., ...). Used by the deterministic parser — PARSING direction only
(source form -> canonical term). Rendering uses the canonical output templates,
not this table, so the two never drift apart.

Implementation notes for Phase 4:
- Multi-word keys ("UNS PTNS") will not survive naive single-token lookup; the
  parser must try multi-word matches before splitting on whitespace.
- Keys appear with and without trailing periods and in mixed case ("Sec.",
  "SEC.S"); normalize before lookup.
"""

from __future__ import annotations

# Indicative starter map; expand from docs/parsing_complexity.md during Phase 4.
ABBREVIATIONS: dict[str, str] = {
    "PCL": "Parcel",
    "BLK": "Block",
    "PL": "Plan",
    "SEC": "Section",
    "SECS": "Sections",
    "SEC.S": "Sections",
    "RGE": "Range",
    "RGES": "Ranges",
    "TWP": "Township",
    "DIST": "District",
    "DL": "District Lot",
    "LT": "Lot",
    "LTS": "Lots",
    "SL": "Sublot",
    "PT": "Part",
    "PTN": "Portion",
    "PTNS": "Portions",
    "EX": "Except",
    "EXC": "Except",
    "UNS": "Unsurveyed",
    "UNS PTNS": "Unsurveyed Portions",
}
