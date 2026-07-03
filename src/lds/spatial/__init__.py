"""Spatial stage (Stage 1).

Resolves a tenure to a canonical polygon, overlays it against the BCGW survey
fabric in Oracle, and produces a StructuredOverlap. Needs Oracle and GeoPandas.

This package depends on lds.contracts. It must NOT import lds.engine — the text
engine consumes the contract this stage produces, but the two never import each
other.
"""
