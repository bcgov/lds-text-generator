"""Optional Ollama-backed implementation of the ParserBackend interface.

Used only for the residual hard strings the deterministic parser marks unparsed.
Disabled by default. Guarded by a timeout / resource check so it degrades to
"could not parse" (-> flag for manual entry) rather than hanging on constrained
hardware. Runs locally; the model and weights are not bundled with the tool.

This module may import an Ollama client. The engine must NOT import this module
directly — it is injected via parser_interface.resolve_backend.
"""

from __future__ import annotations

from lds.constants import LLM_TIMEOUT_SECONDS
from lds.contracts.overlap import ParsedComponents


class OllamaParser:
    """ParserBackend backed by a local Ollama model. Opt-in."""

    def __init__(self, model: str, timeout_s: float = LLM_TIMEOUT_SECONDS) -> None:
        self.model = model
        self.timeout_s = timeout_s

    def available(self) -> bool:
        """True if a local Ollama server is reachable and the model can load.
        Used to decide whether to offer the fallback; never required."""
        raise NotImplementedError("Phase 7: probe local Ollama availability")

    def parse(self, legal_description: str) -> ParsedComponents:
        """Attempt to parse a hard string. On timeout / unavailability / low
        confidence, return ParsedComponents(unparsed=True)."""
        raise NotImplementedError("Phase 7: prompt local model; guard with timeout; never raise")
