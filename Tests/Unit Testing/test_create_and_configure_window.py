import os
import sys
import tkinter
from unittest.mock import patch
from tkinter import ttk  # noqa: F401

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__), '../../../sources/Overwatch Rank Tracker')))
import MainWindow   # noqa: E402


def setup_main_window_with_mock():
    """Running the 'create_and_configure_window' function using mocking,
     as the 'iconphoto' method cannot be called within unit testing, due to the absence of an actual application window."""

    # creating an instance of a class
    mainWindow = MainWindow.MainWindow()

    # since there is no actual window in the tests, the "iconphoto" method cannot be applied, so it is mocked here
    with patch.object(tkinter.Tk, 'iconphoto'):
        mainWindow.create_and_configure_window()

    return mainWindow


def test_window_created():
    """Checking that the window is actually created."""

    mainWindow = setup_main_window_with_mock()
    assert isinstance(mainWindow.main_window, tkinter.Tk)


def test_window_title():
    """Checking that the window has the desired name."""

    mainWindow = setup_main_window_with_mock()
    assert mainWindow.main_window.title() == 'Overwatch Rank Tracker'


def test_window_style():
    """Checking that the styles have been configured correctly."""

    mainWindow = setup_main_window_with_mock()

    # get styles
    style = tkinter.ttk.Style(mainWindow.main_window)
    actual_styles = {'background': style.lookup('Treeview', 'background'), 'foreground': style.lookup('Treeview', 'foreground'), 'fieldbackground': style.lookup('Treeview', 'fieldbackground')}
    expected_styles = {'background': '#2B2B2B', 'foreground': 'white', 'fieldbackground': '#2B2B2B'}

    assert actual_styles == expected_styles
