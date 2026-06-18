"""HandoverGap RAG public API."""

__version__ = "1.0.0"

from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.core.gate import ContextReadinessGate, TransferabilityGate
from handovergap.judge import load_llm_judge_rubric
from handovergap.planning import FollowupRetrievalQuery, build_followup_retrieval_queries
from handovergap.privacy import PrivacyFinding, scan_privacy
from handovergap.profiles import (
    ProfileCatalog,
    ProfileDefinition,
    ProfileValidationResult,
    SlotPolicy,
    validate_profile_file,
)
from handovergap.routing import (
    DeploymentMode,
    ProductRoute,
    RetrievalMode,
    RouteAction,
    SafetyPolicy,
    route_transferability_result,
)
from handovergap.schemas import FollowupRetrievalMetrics
from handovergap.slot_filling_modes import SLOT_FILL_MODE_DESCRIPTIONS, SlotFillMode
from handovergap.slot_mapping import map_evidence_slots_by_keywords
from handovergap.store import InMemoryStore
from handovergap.stores import TiDBSchemaState, TiDBStore, TiDBStoreOperationError
from handovergap.user_dataset import export_annotation_template, import_reviewed_labels, load_user_dataset

__all__ = [
    "ContextReadinessGate",
    "HandoverGapDetector",
    "HandoverGapEvaluator",
    "FollowupRetrievalQuery",
    "FollowupRetrievalMetrics",
    "InMemoryStore",
    "ProfileCatalog",
    "ProfileDefinition",
    "ProfileValidationResult",
    "ProductRoute",
    "PrivacyFinding",
    "DeploymentMode",
    "RetrievalMode",
    "RouteAction",
    "SafetyPolicy",
    "SlotPolicy",
    "SlotFillMode",
    "SLOT_FILL_MODE_DESCRIPTIONS",
    "TiDBSchemaState",
    "TiDBStore",
    "TiDBStoreOperationError",
    "TransferabilityGate",
    "__version__",
    "map_evidence_slots_by_keywords",
    "build_followup_retrieval_queries",
    "export_annotation_template",
    "import_reviewed_labels",
    "load_user_dataset",
    "load_llm_judge_rubric",
    "route_transferability_result",
    "scan_privacy",
    "validate_profile_file",
]
