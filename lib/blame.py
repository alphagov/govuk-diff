from typing import List
from lib.edition_with_changenote import EditionWithChangeNote


def change_note_for(line: str, editions: List[EditionWithChangeNote]) -> str:
    for [idx, e] in enumerate(editions):
        if line not in e.lines:
            return editions[idx - 1].change_note
    return editions[-1].change_note
