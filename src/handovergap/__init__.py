"""HandoverGap RAG public API."""

__version__ = "0.1.18"

from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.core.gate import ContextReadinessGate, TransferabilityGate
from handovergap.privacy import PrivacyFinding, scan_privacy
from handovergap.profiles import (
    ProfileCatalog,
    ProfileDefinition,
    ProfileValidationResult,
    SlotPolicy,
    validate_profile_file,
)
from handovergap.routing import ProductRoute, route_transferability_result
from handovergap.slot_filling_modes import SLOT_FILL_MODE_DESCRIPTIONS, SlotFillMode
from handovergap.slot_mapping import map_evidence_slots_by_keywords
from handovergap.store import InMemoryStore
from handovergap.stores import TiDBStore
from handovergap.user_dataset import export_annotation_template, import_reviewed_labels, load_user_dataset

__all__ = [
    "ContextReadinessGate",
    "HandoverGapDetector",
    "HandoverGapEvaluator",
    "InMemoryStore",
    "ProfileCatalog",
    "ProfileDefinition",
    "ProfileValidationResult",
    "ProductRoute",
    "PrivacyFinding",
    "SlotPolicy",
    "SlotFillMode",
    "SLOT_FILL_MODE_DESCRIPTIONS",
    "TiDBStore",
    "TransferabilityGate",
    "__version__",
    "map_evidence_slots_by_keywords",
    "export_annotation_template",
    "import_reviewed_labels",
    "load_user_dataset",
    "route_transferability_result",
    "scan_privacy",
    "validate_profile_file",
]
