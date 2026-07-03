"""Text engine (Stage 2).

Consumes a StructuredOverlap and produces the legal description. PURE Python:
no Oracle, no GeoPandas, no Dash, no web imports. This is what lets the engine be
tested in isolation against golden fixtures with no database and no server.

The optional language model is reached only through parser_interface.ParserBackend;
the engine never imports Ollama or any model library directly.
"""
