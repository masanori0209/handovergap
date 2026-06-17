"""HandoverGap RAG public API."""

__version__ = "0.1.8"

from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.core.gate import ContextReadinessGate, TransferabilityGate
from handovergap.profiles import ProfileCatalog, ProfileDefinition, SlotPolicy
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
]
