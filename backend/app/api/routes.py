import hashlib
import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.entities import AuditRecord, Document, Verification
from app.schemas.api import AnalyzeRequest, AuditResponse, DashboardStatistics, ExplanationResponse, FaceMatchRequest, Signal, UploadResponse, VerificationResponse
from app.services.analysis.demo import DeterministicDemoAnalyzer, DeterministicDemoFaceMatcher
from app.services.audit.ledger import record_verification
from app.services.risk.engine import score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "application/pdf"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}


def get_document(document_id: str, db: Session) -> Document:
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(404, "Document not found.")
    return document


def get_verification(verification_id: str, db: Session) -> Verification:
    verification = db.get(Verification, verification_id)
    if not verification:
        raise HTTPException(404, "Verification not found.")
    return verification


def verification_response(item: Verification) -> VerificationResponse:
    return VerificationResponse(id=item.id, document_id=item.document_id, status=item.status, decision=item.decision, risk_score=item.risk_score, signals=item.signals, created_at=item.created_at)


@router.post("/documents/upload", response_model=UploadResponse, status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> UploadResponse:
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()
    if not filename or suffix not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "Only PNG, JPEG, and PDF synthetic test documents are accepted.")
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    target = settings.upload_dir / f"{uuid4()}{suffix}"
    digest = hashlib.sha256()
    written = 0
    try:
        with target.open("xb") as output:
            while chunk := await file.read(64 * 1024):
                written += len(chunk)
                if written > settings.max_upload_bytes:
                    raise HTTPException(413, "Upload exceeds the configured size limit.")
                digest.update(chunk)
                output.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    existing = db.scalar(select(Document).where(Document.sha256 == digest.hexdigest()))
    if existing:
        target.unlink(missing_ok=True)
        logger.info("Reused duplicate synthetic document id=%s", existing.id)
        return UploadResponse(document_id=existing.id, filename=existing.original_filename, sha256=existing.sha256, byte_size=existing.byte_size)
    document = Document(original_filename=filename, content_type=file.content_type, storage_path=str(target.resolve()), sha256=digest.hexdigest(), byte_size=written)
    db.add(document); db.commit(); db.refresh(document)
    logger.info("Uploaded synthetic test document id=%s bytes=%s", document.id, written)
    return UploadResponse(document_id=document.id, filename=document.original_filename, sha256=document.sha256, byte_size=document.byte_size)


@router.post("/documents/{document_id}/analyze", response_model=VerificationResponse, status_code=201)
def analyze_document(document_id: str, payload: AnalyzeRequest, db: Session = Depends(get_db)) -> VerificationResponse:
    document = get_document(document_id, db)
    signals = DeterministicDemoAnalyzer().analyze(document.original_filename, payload.demo_scenario)
    risk_score, decision, signals = score(signals)
    verification = Verification(document_id=document.id, decision=decision.value, risk_score=risk_score, signals=[signal.model_dump() for signal in signals])
    db.add(verification); db.flush(); record_verification(db, document, verification); db.commit(); db.refresh(verification)
    logger.info("Analysis complete verification=%s decision=%s risk=%s", verification.id, decision.value, risk_score)
    return verification_response(verification)


@router.post("/verification/{verification_id}/face-match", response_model=VerificationResponse)
def face_match(verification_id: str, payload: FaceMatchRequest, db: Session = Depends(get_db)) -> VerificationResponse:
    verification = get_verification(verification_id, db)
    signals = [item for item in verification.signals if item["id"] not in {"face", "critical_escalation"}]
    signals.append(DeterministicDemoFaceMatcher().compare(payload.demo_outcome).model_dump())
    typed = [Signal.model_validate(item) for item in signals]
    verification.risk_score, decision, typed = score(typed); verification.decision = decision.value; verification.signals = [item.model_dump() for item in typed]
    db.commit(); db.refresh(verification)
    return verification_response(verification)


@router.get("/verification/{verification_id}", response_model=VerificationResponse)
def read_verification(verification_id: str, db: Session = Depends(get_db)) -> VerificationResponse: return verification_response(get_verification(verification_id, db))


@router.get("/verification/{verification_id}/explanation", response_model=ExplanationResponse)
def explanation(verification_id: str, db: Session = Depends(get_db)) -> ExplanationResponse:
    item = get_verification(verification_id, db)
    summary = "No critical deterministic demo signals were recorded." if item.decision == "VERIFIED" else "Critical or uncertain deterministic demo signals require a verifier decision."
    return ExplanationResponse(verification_id=item.id, decision=item.decision, risk_score=item.risk_score, summary=summary, signals=item.signals)


@router.get("/verifications", response_model=list[VerificationResponse])
def list_verifications(db: Session = Depends(get_db)) -> list[VerificationResponse]: return [verification_response(item) for item in db.scalars(select(Verification).order_by(Verification.created_at.desc())).all()]


@router.get("/dashboard/statistics", response_model=DashboardStatistics)
def statistics(db: Session = Depends(get_db)) -> DashboardStatistics:
    rows = db.execute(select(Verification.decision, func.count(Verification.id)).group_by(Verification.decision)).all()
    total = sum(count for _, count in rows); average = db.scalar(select(func.avg(Verification.risk_score)))
    return DashboardStatistics(total_verifications=total, decisions={decision: count for decision, count in rows}, average_risk_score=round(float(average), 2) if average is not None else None)


@router.get("/audit/{verification_id}", response_model=AuditResponse)
def audit(verification_id: str, db: Session = Depends(get_db)) -> AuditResponse:
    entry = db.scalar(select(AuditRecord).where(AuditRecord.verification_id == verification_id))
    if not entry: raise HTTPException(404, "Audit record not found.")
    return AuditResponse(verification_id=entry.verification_id, document_hash=entry.document_hash, result_hash=entry.result_hash, previous_hash=entry.previous_hash, created_at=entry.created_at)
