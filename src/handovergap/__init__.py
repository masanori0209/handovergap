"""HandoverGap RAG public API."""

__version__ = "0.1.9"

from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.core.gate import ContextReadinessGate, TransferabilityGate
from handovergap.profiles import ProfileCatalog, ProfileDefinition, SlotPolicy
from handovergap.slot_mapping import map_evidence_slots_by_keywords
from handovergap.store import InMemoryStore
from handovergap.stores import TiDBStore

__all__ = [
    "ContextReadinessGate",
    "HandoverGapDetector",
    "HandoverGapEvaluator",
    "InMemoryStore",
    "ProfileCatalog",
    "ProfileDefinition",
    "SlotPolicy",
    "TiDBStore",
    "TransferabilityGate",
    "__version__",
    "map_evidence_slots_by_keywords",
]
