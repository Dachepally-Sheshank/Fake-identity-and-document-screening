from app.schemas.api import Decision, Signal


def score(signals: list[Signal]) -> tuple[int, Decision, list[Signal]]:
    """Explainable deterministic aggregation; severe fraud evidence cannot be diluted by averaging."""
    base = round(sum(item.score for item in signals) / len(signals)) if signals else 0
    critical = next((item for item in signals if item.id in {"forensics", "face"} and item.score >= 60), None)
    if critical:
        final = max(70, min(95, critical.score + 15))
        signals = [*signals, Signal(id="critical_escalation", label="Critical-evidence escalation", score=final, status="error", detail=f"{critical.label} crossed the critical threshold ({critical.score}/100), so final risk is escalated.")]
    else:
        final = base
    decision = Decision.HIGH_RISK if final >= 60 else Decision.MANUAL_REVIEW if final >= 25 else Decision.VERIFIED
    return final, decision, signals
