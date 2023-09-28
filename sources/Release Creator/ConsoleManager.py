import sys

import TokenManager
import UploadReleaseAsset
import BuildAndArchiveManager


class ConsoleManager:

    @staticmethod
    def run(token: str, zip_file_path: str, project_directory_path: str, owner_name, repo_name):
        """Displaying a dialog box in the console to control its commands."""

        while True:
            userChoice = input("\nSelect the desired command:\n"
                               "1. Create a release of current project.\n"
                               "2. Add token to project.\n"
                               "3. Build project.\n"
                               "4. Archive build.\n"
                               "5. Delete token from project.\n"
                               "6. Exit.\n\n"
                               "Select an option: ")

            # 1. Create a release of current project
            if userChoice == '1':

                # add token
                tokenManager = TokenManager.TokenManager(token=token, project_directory_path=project_directory_path)
                tokenManager.add_token_to_project()

                # build and archive
                buildAndArchive = BuildAndArchiveManager.BuildAndArchiveManager(project_directory_path=project_directory_path)
                buildAndArchive.build_project(zip_file_path=zip_file_path)
                buildAndArchive.archive_build()

                # upload release
                uploadReleaseAsset = UploadReleaseAsset.UploadReleaseAsset(owner_name=owner_name, repo_name=repo_name, zip_file_path=zip_file_path, token=token)
                uploadReleaseAsset.run()

                # delete token
                tokenManager.delete_token_from_project()

            # 2. Add token to project
            elif userChoice == '2':
                tokenManager = TokenManager.TokenManager(token=token, project_directory_path=project_directory_path)
                tokenManager.add_token_to_project()

            # 3. Build project
            elif userChoice == '3':
                buildAndArchive = BuildAndArchiveManager.BuildAndArchiveManager(project_directory_path=project_directory_path)
                buildAndArchive.build_project(zip_file_path=zip_file_path)

            # 4. Archive build
            elif userChoice == '4':
                try:
                    buildAndArchive = BuildAndArchiveManager.BuildAndArchiveManager(project_directory_path=project_directory_path)
                    buildAndArchive.archive_build()
                    print('WARNING: You used "Archive build" directly, be careful as this function makes an archive from a build that was previously created, '
                          'its version may not be up to date if you did not use the "Build project" function before.')
                except FileNotFoundError as error:
                    print(error)

            # 5. Delete token from project
            elif userChoice == '5':
                tokenManager = TokenManager.TokenManager(token=token, project_directory_path=project_directory_path)
                tokenManager.delete_token_from_project()

            elif userChoice == '6':
                sys.exit()

            else:
                print('Invalid input. Try again.')
