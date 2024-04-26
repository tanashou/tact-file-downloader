from dataclasses import dataclass


@dataclass
class SakaiContent:
    title: str
    type: str
    url: str
    size: int
