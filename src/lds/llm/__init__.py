"""Optional model-backed parser fallback. Opt-in, disabled by default. The engine
reaches this only through engine.parser_interface.ParserBackend; nothing in the
engine imports this package directly. The model and its weights live OUTSIDE the
tool folder (Ollama runtime + cache); see the project plan section 2.6a."""
