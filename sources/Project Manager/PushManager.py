import subprocess
import time


class PushManager:

    @staticmethod
    def __git_add():
        """Executing terminal command - git add ."""

        subprocess.run(["git", "add", "."])

    def push_new_commit(self, commit_message: str):
        """Commands to create a new commit."""

        self.__git_add()
        subprocess.run(["git", "commit", "-m", commit_message])
        subprocess.run(["git", "push", "origin", "master"])
        time.sleep(3)

    def push_replacing_last_commit(self, commit_message: str = None):
        """Commands to replace last commit and possibly its message."""

        self.__git_add()

        # without replacing commit message
        if commit_message is None:
            subprocess.run(["git", "commit", "--amend", "-C", "HEAD"])

        # replacing commit message
        else:
            subprocess.run(["git", "commit", "--amend", "-m", commit_message])

        subprocess.run(["git", "push", "--force"])
        time.sleep(3)
