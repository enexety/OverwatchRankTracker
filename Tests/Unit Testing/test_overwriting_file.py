import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__), '../../../sources/Overwatch Rank Tracker')))
import FileManager  # noqa: E402


"""
Writing a test for another path does not make sense since the user does not have access to this.

It also doesn't make sense to write a test for the wrong file that was modified earlier by the user. Since when adding information to a text widget
 that goes when creating the main window, it is checked for a changed file and it is overwritten if something happens.
"""


# global variables
path_to_file_test = os.path.join(os.path.dirname(sys.argv[0]), 'test_settings_and_battle_tags.json')


def test_overwriting_max_workers_correct_file():
    """Overwrite max_workers with correct file."""

    # define a class
    fileManager = FileManager.FileManager()

    # value change
    fileManager.path_to_file = path_to_file_test
    fileManager.max_workers = 3

    # create file
    fileManager.write_file(paste={"Settings": {"max_workers": 5}, "Battle-tags": []})

    # rewrite value of max_workers
    fileManager.overwriting_file(max_workers_bool=True)

    # check
    assert fileManager.read_file()['Settings']['max_workers'] == 3

    # delete file
    os.remove(path_to_file_test)


def test_overwriting_battle_tags():
    """Overwrite battle-tags with correct file."""

    # define a class
    fileManager = FileManager.FileManager()

    # value change
    fileManager.path_to_file = path_to_file_test

    # create file
    fileManager.write_file(paste={"Settings": {"max_workers": 3}, "Battle-tags": []})

    # rewrite value of battle_tags
    fileManager.overwriting_file(battle_tags_bool=True, battle_tags=['example-1234', 'other-2345', 'more-3456'])

    # check
    assert fileManager.read_file()['Battle-tags'] == ['example-1234', 'other-2345', 'more-3456']

    # delete file
    os.remove(path_to_file_test)


def test_full_rewrite():
    """Overwrite full file in initial settings with file."""

    # define a class
    fileManager = FileManager.FileManager()

    # value change
    fileManager.path_to_file = path_to_file_test

    # rewrite full file
    fileManager.overwriting_file(full_rewrite=True)

    # check
    assert fileManager.read_file() == {"Settings": {"max_workers": 6}, "Battle-tags": [""]}

    # delete file
    os.remove(path_to_file_test)
