import json
import os.path
import sys


class FileManager:

    def __init__(self):
        self.max_workers = 6
        self.path_to_file = os.path.join(os.path.dirname(sys.argv[0]), 'settings_and_battle_tags.json')

    def read_file(self):
        """Returns the contents of a file."""

        with open(self.path_to_file, 'r') as file:
            return json.load(file)

    def write_file(self, paste: dict):
        """Record file with new content."""

        with open(self.path_to_file, 'w') as file:
            json.dump(paste, file, indent=2)

    def overwriting_file(self, max_workers_bool: bool = False, battle_tags_bool: bool = False, battle_tags: list = None, full_rewrite: bool = False):
        """Overwrite file or certain blocks in file."""

        if battle_tags is None:
            battle_tags = [""]

        # file exists
        try:

            # call error for rewrite file
            if full_rewrite:
                raise FileNotFoundError

            # read file and rewrite certain settings
            file_content = self.read_file()
            if max_workers_bool:
                file_content["Settings"]["max_workers"] = int(self.max_workers)
            if battle_tags_bool:
                file_content["Battle-tags"] = battle_tags
            if max_workers_bool or battle_tags_bool:
                self.write_file(paste=file_content)

        # file do not exist or need to rewrite it
        except FileNotFoundError:
            self.write_file(paste={"Settings": {"max_workers": int(self.max_workers)}, "Battle-tags": battle_tags})

    def set_settings(self):
        """Set settings for further use in the code."""

        try:

            # read file
            file_content = self.read_file()

            # set settings
            self.max_workers = file_content['Settings']['max_workers']

        # file changed outside or not exist - rewrite the file
        except (json.decoder.JSONDecodeError, FileNotFoundError, AttributeError):
            self.overwriting_file(full_rewrite=True)
