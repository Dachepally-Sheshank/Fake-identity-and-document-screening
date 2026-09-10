from app.schemas.api import DemoScenario, FaceOutcome, Signal
from app.services.analysis.contracts import DocumentAnalyzer, FaceMatcher


class DeterministicDemoAnalyzer(DocumentAnalyzer):
    """Temporary adapter. Replace with OpenCV/OCR models without changing routes."""
    def analyze(self, filename: str, scenario: DemoScenario) -> list[Signal]:
        normalized = filename.lower()
        if scenario is DemoScenario.AUTO:
            scenario = DemoScenario.TAMPERED if any(word in normalized for word in ("fake", "tamper", "forg", "manipulat", "edit")) else DemoScenario.BLURRED if any(word in normalized for word in ("blur", "unclear", "low-quality")) else DemoScenario.GENUINE
        signals = [
            Signal(id="quality", label="Document quality", score=4, status="success", detail="Demo image-quality heuristic found no low-quality marker."),
            Signal(id="ocr", label="OCR extraction", score=3, status="success", detail="Demo OCR adapter returned a stable synthetic extraction."),
            Signal(id="forensics", label="Document forensics", score=2, status="success", detail="Demo forensic adapter found no configured anomaly."),
        ]
        if scenario is DemoScenario.BLURRED:
            signals[0] = Signal(id="quality", label="Document quality", score=42, status="warning", detail="Demo low-quality marker triggered a readability concern.")
            signals[1] = Signal(id="ocr", label="OCR extraction", score=26, status="warning", detail="Demo low-quality marker reduced extraction confidence.")
        if scenario is DemoScenario.TAMPERED:
            signals[2] = Signal(id="forensics", label="Document forensics", score=70, status="error", detail="Demo tamper marker triggered simulated edit-boundary and font-consistency evidence.")
        return signals


class DeterministicDemoFaceMatcher(FaceMatcher):
    def compare(self, outcome: FaceOutcome) -> Signal:
        values = {
            FaceOutcome.MATCH: (5, "success", "Demo face-match adapter reports matching synthetic references."),
            FaceOutcome.INCONCLUSIVE: (35, "warning", "Demo face-match adapter cannot determine a synthetic match."),
            FaceOutcome.MISMATCH: (78, "error", "Demo face-match adapter reports a synthetic face mismatch."),
        }
        score, status, detail = values[outcome]
        return Signal(id="face", label="Face comparison", score=score, status=status, detail=detail)
