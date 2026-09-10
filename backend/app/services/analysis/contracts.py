from abc import ABC, abstractmethod

from app.schemas.api import DemoScenario, FaceOutcome, Signal


class DocumentAnalyzer(ABC):
    @abstractmethod
    def analyze(self, filename: str, scenario: DemoScenario) -> list[Signal]: ...


class FaceMatcher(ABC):
    @abstractmethod
    def compare(self, outcome: FaceOutcome) -> Signal: ...
