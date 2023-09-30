import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__), '../../../sources/Overwatch Rank Tracker')))
import FileManager  # noqa: E402


path_to_file_test = os.path.abspath(os.path.join(__file__, '../../test_settings_and_battle_tags.json'))


def test_set_settings_value_change():
    """Checks for changes to settings variables after using the "set_settings" function."""

    # define a class
    filemanager = FileManager.FileManager()

    # value change
    filemanager.path_to_file = path_to_file_test
    filemanager.max_workers = 3

    # create file
    filemanager.overwriting_file(full_rewrite=True)

    # value change, max_workers in file = 3, in class = 6
    filemanager.max_workers = 6

    # set settings, max_workers should now be set to 2
    filemanager.set_settings()

    # delete file
    os.remove(path_to_file_test)

    assert filemanager.max_workers == 3


def test_set_settings_no_file():
    """Checks that after using the "set_settings" function a file with settings is created, if it was not there before."""

    # define a class
    filemanager = FileManager.FileManager()

    # value change
    filemanager.path_to_file = path_to_file_test

    # set settings, max_workers should now be set to 2
    filemanager.set_settings()

    assert os.path.exists(filemanager.path_to_file)

    # delete file
    os.remove(path_to_file_test)
