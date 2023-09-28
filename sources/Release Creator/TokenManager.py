import os
import re


class TokenManager:

    def __init__(self, token, project_directory_path):
        self.project_base_class_path = os.path.join(project_directory_path, 'sources', 'Overwatch Rank Tracker', 'OverwatchRankTracker.py')
        self.token = token

    def add_token_to_project(self):
        """Adds a token to base class of project."""

        # read the contents of project base class
        with open(self.project_base_class_path, 'r') as file:
            file_content = file.read()

        # replace token in project base class
        file_content = re.sub(r'self.token = "[^"]*"', f'self.token = "{self.token}"', file_content)

        # rewrite token in project base class
        with open(self.project_base_class_path, 'w') as f:
            f.write(file_content)

        print('\nToken has been added.')

    def delete_token_from_project(self):
        """Deletes a token from project's base class."""

        # read functions.py
        with open(self.project_base_class_path, 'r') as file:
            file_content = file.read()

        # replace token in functions.py
        file_content = re.sub(r'self.token = "[^"]*"', 'self.token = ""', file_content)

        # rewrite token in functions.py
        with open(self.project_base_class_path, 'w') as file:
            file.write(file_content)

        print('\nToken has been deleted.')

    @staticmethod
    def get_token(token_file_path: str, token: str):
        """If token is not specified directly, but for example path to it is specified, it gets token from a local file."""

        # get token from file
        if token == '' and token_file_path != '':

            # file exists
            if os.path.exists(token_file_path):

                # read local file with token
                with open(token_file_path, 'r') as file:
                    file_content = file.read()

                # find token
                match = re.search(r'ghp_\S+', file_content)

                # token found - write it down
                if match:
                    token = match.group(0)

                # token not found - error
                else:
                    raise FileNotFoundError('Incorrect token. By GitHub standards, token starts with "ghp_".')

            # file not exists - error
            else:
                raise FileNotFoundError(f'Incorrect token file path. The file does not exist. Path - "{token_file_path}"')

        # variables are not set
        elif token == '' and token_file_path == '':
            raise ValueError('Please enter configuration settings of token or its paths in the "config.ini" file, it is located at this path "Overwatch_Rank_Tracker/resources"')

        return token
