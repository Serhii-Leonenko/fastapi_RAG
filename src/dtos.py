from dataclasses import dataclass


@dataclass(frozen=True)
class FileResult:
    filename: str
    chunks: list[str]
