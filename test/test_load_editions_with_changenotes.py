from lib.load_editions_with_changenotes import load_from_hardcoded_data
def test_load_from_hardcoded_data():
    editions = load_from_hardcoded_data()
    assert(len(editions)) == 17
    assert editions[0].id == 8578044
    assert editions[16].id == 679139
