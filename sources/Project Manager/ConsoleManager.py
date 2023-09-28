import sys

import TokenManager
import UploadReleaseAsset
import BuildAndArchiveManager
import PushManager


class ConsoleManager:

    def __init__(self):
        self.pushManager = None
        self.tokenManager = None
        self.buildAndArchive = None
        self.uploadReleaseAsset = None

    def run(self, token: str, zip_file_path: str, project_directory_path: str, owner_name, repo_name):
        """Displaying a dialog box in the console to control its commands."""

        while True:
            userChoice = input("\nSelect the desired command:\n"
                               "1. Push project with creation of a new commit.\n"
                               "2. Push project, replacing the last commit.\n"
                               "3. Create a release of current project.\n"
                               "4. Add token to project.\n"
                               "5. Build project.\n"
                               "6. Archive build.\n"
                               "7. Delete token from project.\n"
                               "8. Exit.\n\n"
                               "Select an option: ")

            # 1. Push project with creation of a new commit
            if userChoice == '1':
                self.push_with_creation_new_commit()

            # 2. Push project, replacing the last commit
            elif userChoice == '2':
                self.push_replacing_last_commit()

            # 3. Create a release of current project
            elif userChoice == '3':
                self.create_release(token=token, project_directory_path=project_directory_path, zip_file_path=zip_file_path, owner_name=owner_name, repo_name=repo_name)

            # 4. Add token to project
            elif userChoice == '4':
                if self.tokenManager is None:
                    self.tokenManager = TokenManager.TokenManager(token=token, project_directory_path=project_directory_path)
                self.tokenManager.add_token_to_project()

            # 5. Build project
            elif userChoice == '5':
                if self.buildAndArchive is None:
                    self.buildAndArchive = BuildAndArchiveManager.BuildAndArchiveManager(project_directory_path=project_directory_path)
                self.buildAndArchive.build_project(zip_file_path=zip_file_path)

            # 6. Archive build
            elif userChoice == '6':
                try:
                    if self.buildAndArchive is None:
                        self.buildAndArchive = BuildAndArchiveManager.BuildAndArchiveManager(project_directory_path=project_directory_path)
                    self.buildAndArchive.archive_build()
                    print('WARNING: You used "Archive build" directly, be careful as this function makes an archive from a build that was previously created, '
                          'its version may not be up to date if you did not use the "Build project" function before.')
                except FileNotFoundError as error:
                    print(error)

            # 7. Delete token from project
            elif userChoice == '7':
                if self.tokenManager is None:
                    self.tokenManager = TokenManager.TokenManager(token=token, project_directory_path=project_directory_path)
                self.tokenManager.delete_token_from_project()

            # 8. Exit
            elif userChoice == '8':
                sys.exit()

            else:
                print('Invalid input. Try again.')

    def push_with_creation_new_commit(self):
        """Creating a new commit of current project."""

        while True:
            userChoice = input('Are you sure you want to push project with creation of a new commit? (y/n): ')

            # answer is not y/n
            if (userChoice.isdigit()) or ((userChoice.lower() != 'y') and (userChoice.lower() != 'n')):
                print('\nInvalid input. Try again.')

            # user wants to finish
            if userChoice.lower() == 'n':
                break

            # user wants to continue
            elif userChoice.lower() == 'y':
                commit_message = input("\nCommands:"
                                       "\n1. Back\n"
                                       "\nCommit message: ")

                # user wants to finish
                if commit_message == '1':
                    break

                # create new commit
                if self.pushManager is None:
                    self.pushManager = PushManager.PushManager()
                self.pushManager.push_new_commit(commit_message=commit_message)

                # loop exit
                break

    def push_replacing_last_commit(self):
        """Changing contents of last commit and, if necessary, changing its message."""

        while True:
            userChoice = input('Are you sure you want to push project, replacing the commit? (y/n): ')

            # answer is not y/n
            if (userChoice.isdigit()) or ((userChoice.lower() != 'y') and (userChoice.lower() != 'n')):
                print('\nInvalid input. Try again.')

            # user wants to finish
            if userChoice.lower() == 'n':
                break

            # user wants to continue
            elif userChoice.lower() == 'y':
                while True:
                    userChoice = input('\nCommands:'
                                       "\n1. Back\n"
                                       '\nAre you want to change last commit message? (y/n): ')

                    # user wants to finish
                    if userChoice == '1':
                        break

                    # creating an instance of a class
                    if self.pushManager is None:
                        self.pushManager = PushManager.PushManager()

                    # answer is not y/n
                    if (userChoice.isdigit()) or ((userChoice.lower() != 'y') and (userChoice.lower() != 'n')):
                        print('\nInvalid input. Try again.')

                    # user does not want to change commit message
                    if userChoice.lower() == 'n':
                        self.pushManager.push_replacing_last_commit()
                        break

                    # user wants to change last commit message
                    elif userChoice.lower() == 'y':
                        replacing_commit_message = input('\nCommands:'
                                                         "\n1. Back\n"
                                                         '\nAre you want to change last commit message? (y/n): ')

                        # user wants to finish
                        if replacing_commit_message == '1':
                            break

                        # replace last commit
                        self.pushManager.push_replacing_last_commit(commit_message=replacing_commit_message)

                        # loop exit
                        break

                # loop exit
                break

    def create_release(self, token, project_directory_path, zip_file_path, owner_name, repo_name):
        """Create a release of current project."""

        while True:
            userChoice = input('Are you sure you want to upload current project to repository? (y/n): ')

            # # answer is not y/n
            if (userChoice.isdigit()) or ((userChoice.lower() != 'y') and (userChoice.lower() != 'n')):
                print('\nInvalid input. Try again.')

            # user wants to finish
            if userChoice.lower() == 'n':
                break

            # user wants to change last commit message
            elif userChoice.lower() == 'y':

                # add token
                if self.tokenManager is None:
                    self.tokenManager = TokenManager.TokenManager(token=token, project_directory_path=project_directory_path)
                self.tokenManager.add_token_to_project()

                # build and archive
                if self.buildAndArchive is None:
                    self.buildAndArchive = BuildAndArchiveManager.BuildAndArchiveManager(project_directory_path=project_directory_path)
                self.buildAndArchive.build_project(zip_file_path=zip_file_path)
                self.buildAndArchive.archive_build()

                # upload release
                if self.uploadReleaseAsset is None:
                    self.uploadReleaseAsset = UploadReleaseAsset.UploadReleaseAsset(owner_name=owner_name, repo_name=repo_name, zip_file_path=zip_file_path, token=token)
                self.uploadReleaseAsset.run()

                # delete token
                self.tokenManager.delete_token_from_project()

                # loop exit
                break
