"""Deterministic parser: legal-description string -> ParsedComponents.

The default ParserBackend. Handles the real registry forms catalogued in
docs/parsing_complexity.md: heavy abbreviation (PCL.F, BLK.1VL&M, RGES.5&6,
UNS PTNS), except-clauses, fractional/acreage descriptors, multi-district strings,
run-together clauses. Must NEVER raise on bad input — return
ParsedComponents(unparsed=True) so the row is flagged for manual entry.

Where the deterministic parser marks a string unparsed, the optional model
fallback (if enabled) may attempt it — but the engine still runs correctly with
the fallback disabled.
"""

from __future__ import annotations

from lds.contracts.overlap import ParsedComponents


class DeterministicParser:
    """The always-present ParserBackend implementation."""

    def parse(self, legal_description: str) -> ParsedComponents:
        raise NotImplementedError("Phase 4: deterministic parse of a legal-description string")
