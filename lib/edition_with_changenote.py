from dataclasses import dataclass
from typing import List

@dataclass
class EditionWithChangeNote:
    lines: List[str]
    change_note: str
