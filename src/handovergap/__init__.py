"""HandoverGap RAG public API."""

__version__ = "0.1.11"

from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.core.gate import ContextReadinessGate, TransferabilityGate
from handovergap.profiles import ProfileCatalog, ProfileDefinition, SlotPolicy
from handovergap.routing import ProductRoute, route_transferability_result
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
    "ProductRoute",
    "SlotPolicy",
    "TiDBStore",
    "TransferabilityGate",
    "__version__",
    "map_evidence_slots_by_keywords",
    "route_transferability_result",
]
