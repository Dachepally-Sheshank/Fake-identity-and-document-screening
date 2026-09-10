import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import AuditRecord, Document, Verification


def record_verification(db: Session, document: Document, verification: Verification) -> AuditRecord:
    prior = db.scalar(select(AuditRecord).order_by(AuditRecord.created_at.desc()))
    material = json.dumps({"verification_id": verification.id, "decision": verification.decision, "risk_score": verification.risk_score, "signals": verification.signals}, sort_keys=True)
    audit = AuditRecord(verification_id=verification.id, document_hash=document.sha256, result_hash=hashlib.sha256(material.encode()).hexdigest(), previous_hash=prior.result_hash if prior else None)
    db.add(audit)
    return audit
