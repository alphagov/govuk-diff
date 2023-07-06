import datetime
from dataclasses import dataclass
from typing import List

@dataclass
class EditionWithChangeNote:
    lines: List[str]
    created_at: datetime.datetime
    id: int
    change_note: str
