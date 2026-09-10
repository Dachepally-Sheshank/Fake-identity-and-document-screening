from app.schemas.api import Signal
from app.services.risk.engine import score


def test_critical_forgery_signal_escalates_risk():
    risk, decision, signals = score([Signal(id="forensics", label="Document forensics", score=70, status="error", detail="test")])
    assert risk >= 70
    assert decision.value == "HIGH_RISK"
    assert signals[-1].id == "critical_escalation"
