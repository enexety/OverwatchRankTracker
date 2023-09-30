import os
import subprocess


class PushManager:

    @staticmethod
    def __git_add():
        """Executing terminal command - git add."""

        os.chdir('../..')
        subprocess.run(["git", "add", "."], check=True)

    def push_new_commit(self, commit_message: str):
        """Commands to create a new commit."""

        self.__git_add()
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "master"], check=True)

    def push_replacing_last_commit(self, commit_message: str = None):
        """Commands to replace last commit and possibly its message."""

        self.__git_add()

        # without replacing commit message
        if commit_message is None:
            subprocess.run(["git", "commit", "--amend", "-C", "HEAD"], check=True)

        # replacing commit message
        else:
            subprocess.run(["git", "commit", "--amend", "-m", commit_message], check=True)

        subprocess.run(["git", "push", "--force"], check=True)
