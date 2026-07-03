"""The parser interface.

The engine declares this interface and calls it. The deterministic parser
(parse.py) is the default implementation. An optional model-backed implementation
lives in lds.llm.ollama_parser and is INJECTED — the engine never imports Ollama
or any model library.

If no backend resolves a string, the result carries `unparsed=True` and the row is
flagged for manual entry rather than guessed. The model is strictly additive.
"""

from __future__ import annotations

from typing import Protocol

from lds.contracts.overlap import ParsedComponents


class ParserBackend(Protocol):
    """A pluggable parser. Implementations: the deterministic parser (always
    present) and the optional Ollama parser (opt-in, injected)."""

    def parse(self, legal_description: str) -> ParsedComponents:
        """Parse one legal-description string into structured components.

        Must never raise on unparseable input: return ParsedComponents(unparsed=True)
        instead, so the engine can flag the row for manual entry.
        """
        ...


def resolve_backend(
    deterministic: ParserBackend,
    fallback: ParserBackend | None = None,
) -> ParserBackend:
    """Compose the deterministic parser with an optional fallback.

    Returns a backend that tries the deterministic parser first and, only for
    strings it marks unparsed, consults the fallback (if supplied and enabled).
    The composition is itself a ParserBackend so callers see one interface.
    """
    raise NotImplementedError("Phase 4 / Phase 7: compose deterministic + optional fallback")
