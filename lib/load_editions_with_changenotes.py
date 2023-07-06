import datetime
from typing import List
from lib.edition_with_changenote import EditionWithChangeNote

def load_from_hardcoded_data() -> List[EditionWithChangeNote]:
    from os import listdir
    from os.path import isfile, join
    path = "./hardcoded_data"
    all_files = [f for f in listdir(path) if isfile(join(path, f))]
    all_editions = [edition_with_change_note_from("./hardcoded_data" + "/" + file_name) for file_name in all_files]
    return sorted(all_editions, key=lambda edition: edition.created_at, reverse=True)

def edition_with_change_note_from(file_name: str) -> EditionWithChangeNote:
    with open(file_name) as file:
        lines = [l.rstrip() for l in file.readlines()]
        id = int(lines[0])
        created_at = datetime.datetime.strptime(lines[1], "%Y-%m-%d %H:%M:%S.%f")
        ls = lines[2].split("\n")
        change_note = lines[3]
        edition = EditionWithChangeNote(ls, created_at, id, change_note)
    return edition
