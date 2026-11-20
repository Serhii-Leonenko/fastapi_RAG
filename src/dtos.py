from dataclasses import dataclass


@dataclass(frozen=True)
class PDFResult:
    filename: str
    chunks: list[str]
