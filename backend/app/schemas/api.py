from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Decision(str, Enum):
    VERIFIED = "VERIFIED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    HIGH_RISK = "HIGH_RISK"


class DemoScenario(str, Enum):
    AUTO = "auto"; GENUINE = "genuine"; BLURRED = "blurred"; TAMPERED = "tampered"; FACE_MISMATCH = "face_mismatch"


class FaceOutcome(str, Enum):
    MATCH = "match"; MISMATCH = "mismatch"; INCONCLUSIVE = "inconclusive"


class Signal(BaseModel):
    id: str; label: str; score: int = Field(ge=0, le=100); status: str; detail: str; source: str = "deterministic_demo"


class UploadResponse(BaseModel): document_id: str; filename: str; sha256: str; byte_size: int
class AnalyzeRequest(BaseModel): demo_scenario: DemoScenario = DemoScenario.AUTO
class FaceMatchRequest(BaseModel): demo_outcome: FaceOutcome
class VerificationResponse(BaseModel):
    id: str; document_id: str; status: str; decision: Decision; risk_score: int = Field(ge=0, le=100); signals: list[Signal]; created_at: datetime
class ExplanationResponse(BaseModel): verification_id: str; decision: Decision; risk_score: int; summary: str; signals: list[Signal]
class AuditResponse(BaseModel): verification_id: str; document_hash: str; result_hash: str; previous_hash: str | None; created_at: datetime
class DashboardStatistics(BaseModel): total_verifications: int; decisions: dict[str, int]; average_risk_score: float | None
