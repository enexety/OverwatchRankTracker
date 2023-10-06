import MainWindow
import LogManager
import UpdateManager


class OverwatchRankTracker:
    """Base class, runs: logging, update, main application window. It also stores important variables for working with repository and GitHub Gists."""

    def __init__(self):
        self.version = "v0.0.9"
        self.token = ""

        # I do not use variables from config because I do not want to have unnecessary files after building project
        self.owner_name = 'enexety'
        self.repo_name = 'Overwatch_Rank_Tracker'

    def run(self):

        # create logging
        logManager = LogManager.LogManager(owner_name=self.owner_name, token=self.token)

        # check updates
        UpdateManager.UpdateManager(owner_name=self.owner_name, repo_name=self.repo_name).check_for_updates(logManager=logManager, current_version=self.version)

        # launch main-window
        mainWindow = MainWindow.MainWindow(logManager=logManager)
        mainWindow.run()


if __name__ == "__main__":
    app = OverwatchRankTracker()
    app.run()
