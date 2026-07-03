"""Neutral contract package. Depended on by both the spatial and engine stages;
depends on neither. Defines the structured-overlap interchange record."""

from lds.contracts.overlap import (
    SCHEMA_VERSION,
    CandidateFeature,
    DataMaintenanceFlag,
    DetectionSignal,
    FeatureSourceDataset,
    MessageLevel,
    OutOfScopeFlag,
    OutOfScopeReason,
    OverlapParcel,
    ParcelType,
    ParsedComponents,
    RemainderType,
    SourceType,
    StructuredOverlap,
    TextSource,
    UnsurveyedRemainder,
    ValidationMessage,
    WholePart,
)

__all__ = [
    "SCHEMA_VERSION",
    "CandidateFeature",
    "DataMaintenanceFlag",
    "DetectionSignal",
    "FeatureSourceDataset",
    "MessageLevel",
    "OutOfScopeFlag",
    "OutOfScopeReason",
    "OverlapParcel",
    "ParcelType",
    "ParsedComponents",
    "RemainderType",
    "SourceType",
    "StructuredOverlap",
    "TextSource",
    "UnsurveyedRemainder",
    "ValidationMessage",
    "WholePart",
]
