from dataclasses import dataclass


@dataclass(frozen=True)
class PDFResult:
    filename: str
    sentences: list[str]
