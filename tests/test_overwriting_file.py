import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import functions  # noqa: E402


"""
Writing a test for another path does not make sense since the user does not have access to this.

It also doesn't make sense to write a test for the wrong file that was modified earlier by the user. Since when adding information to a text widget
 that goes when creating the main window, it is checked for a changed file and it is overwritten if something happens.
"""


# global variables
path_to_file_test = 'tests/temporarily_settings_and_battle_tags.json'


def test_overwriting_file_max_workers_correct_file():
    """Overwrite max_workers with correct file"""

    # create file
    functions.write_file(path=path_to_file_test, paste={"Settings": {"max_workers": 5}, "Battle-tags": []})

    # change value
    functions.max_workers = 3

    # rewrite value of max_workers
    functions.overwriting_file(max_workers_bool=True, path=path_to_file_test)

    # check
    assert functions.read_file(path=path_to_file_test)['Settings']['max_workers'] == 3

    # delete file
    os.remove(path_to_file_test)


def test_overwriting_file_battle_tags():
    """Overwrite battle-tags with correct file"""

    # create file
    functions.write_file(path=path_to_file_test, paste={"Settings": {"max_workers": 3}, "Battle-tags": []})

    # rewrite value of battle_tags
    functions.overwriting_file(battle_tags_bool=True, battle_tags=['example-1234', 'other-2345', 'more-3456'], path=path_to_file_test)

    # check
    assert functions.read_file(path=path_to_file_test)['Battle-tags'] == ['example-1234', 'other-2345', 'more-3456']

    # delete file
    os.remove(path_to_file_test)


def test_overwriting_file_full_rewrite():
    """Overwrite full file in initial settings with file"""

    # change value
    functions.max_workers = 6

    # rewrite full file
    functions.overwriting_file(full_rewrite=True, path=path_to_file_test)

    # check
    assert functions.read_file(path=path_to_file_test) == {"Settings": {"max_workers": 6}, "Battle-tags": []}

    # delete file
    os.remove(path_to_file_test)
