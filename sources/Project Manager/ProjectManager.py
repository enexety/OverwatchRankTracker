import configparser
import os
import sys

import ConsoleManager
import TokenManager


class ProjectManager:

    def __init__(self):

        # get paths
        self.project_directory_path = os.path.abspath(os.path.join(sys.argv[0], '../../..'))
        self.zip_file_path = os.path.join(self.project_directory_path, "Overwatch Rank Tracker.zip")
        config_file_path = os.path.join(self.project_directory_path, 'resources', 'config.ini')

        # checking existence of a config file
        if not os.path.exists(config_file_path):
            raise FileNotFoundError(f"Error: Configuration file not found. Path - {config_file_path}")

        # setting variables from a config file
        config = configparser.ConfigParser()
        config.read(config_file_path)
        self.token = config.get('Settings', 'token')
        self.token_file_path = config.get('Settings', 'token_file_path')
        self.owner_name = config.get('Settings', 'owner_name')
        self.repo_name = config.get('Settings', 'repo_name')

        # if there is no token, but there is a path to it, it initializes token
        self.token = TokenManager.TokenManager.get_token(token_file_path=self.token_file_path, token=self.token)

    def run(self):
        """Starting a dialog class for selecting commands."""

        consoleManager = ConsoleManager.ConsoleManager()
        consoleManager.run(token=self.token, zip_file_path=self.zip_file_path, project_directory_path=self.project_directory_path, owner_name=self.owner_name, repo_name=self.repo_name)


if __name__ == "__main__":
    projectManager = ProjectManager()
    projectManager.run()
