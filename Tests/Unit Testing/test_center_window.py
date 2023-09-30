import os
import sys
import tkinter

sys.path.append(os.path.abspath(os.path.join(os.path.abspath(__file__), '../../../sources/Overwatch Rank Tracker')))
import MainWindow   # noqa: E402


def test_center_window():
    """Check that the window is created in the center of the screen."""

    # create window
    test_window = tkinter.Tk()

    # calling window centering function
    MainWindow.MainWindow.center_window(window=test_window, window_height=123, window_width=456)

    # getting window coordinates after centering
    x_coord = test_window.winfo_x()
    y_coord = test_window.winfo_y()

    assert (x_coord, y_coord) == (0, 0)
