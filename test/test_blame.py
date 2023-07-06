import datetime
from typing import List
from lib.blame import change_note_for
from lib.edition_with_changenote import EditionWithChangeNote

def test_selects_the_correct_changenote_when_a_line_is_added():
    e1 = create_edition(["New line added", "Another line"], "Change note 1")
    e2 = create_edition(["New line added", "Another line"], "Change note 2")
    e3 = create_edition(["Another line"], "Change note 3")

    assert change_note_for("New line added", [e1, e2, e3]) == e2.change_note

def test_selects_the_correct_changenote_when_a_line_is_changed():
    e1 = create_edition(["Some text"], "Change note 1")
    e2 = create_edition(["Some texzt"], "Change note 2")
    e3 = create_edition(["Some texzt"], "Change note 3")

    assert change_note_for("Some text", [e1, e2, e3]) == e1.change_note

def test_selects_the_oldest_changenote_when_a_line_is_never_changed():
    e1 = create_edition(["Some text"], "Change note 1")
    e2 = create_edition(["Some text"], "Change note 2")
    e3 = create_edition(["Some text"], "Change note 3")

    assert change_note_for("Some text", [e1, e2, e3]) == e3.change_note
def test_selects_latest_change_for_each_line():
    latest_edition = create_edition(
        ["First line", "second line", "third line", "fourth line"],
        "Change note for latest edition")
    edition_3 = create_edition(
        ["First line of the edition", "second line", "third line", "fourth line"],
        "Change note for third edition")
    edition_2 = create_edition(
        ["First line of the edition aha", "second line - of the edition", "third line", "fourth line"],
        "Change note for second edition")
    edition_1 = create_edition(
        ["First line of the edition aha", "second line - of th edition", "third line of the edition", "fourth line"],
        "Change note for first edition")
    editions = [latest_edition, edition_3, edition_2, edition_1]

    expected_change_notes_per_line = [e.change_note for e in [latest_edition, edition_3, edition_2, edition_1]]

    for [idx, line] in enumerate(latest_edition.lines):
        assert change_note_for(line, editions) == expected_change_notes_per_line[idx]


def create_edition(lines: List[str], change_note: str) -> EditionWithChangeNote:
    return EditionWithChangeNote(lines, datetime.datetime.now(), 12345, change_note)