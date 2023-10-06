import os
import zipfile
import requests
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor
import sys
import subprocess
import tkinter

import OverwatchRankTracker


class UpdateManager:
    """Checks for updates and if the user wants to update the program, closes the current process and opens a new one that will perform the update process itself."""

    def __init__(self, owner_name, repo_name):
        self.owner_name = owner_name
        self.repo_name = repo_name

        self.current_folder_path = None
        self.zip_file_path = None
        self.current_folder_name = None

    def check_for_updates(self, logManager, current_version):
        """Checks the current version in the repository against the current version of the application on the computer and runs an external update process if necessary."""

        response = None

        # create window and hide it
        update_window = tkinter.Tk()
        update_window.withdraw()

        try:

            # request for the latest release version
            response = requests.get(f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/releases/latest")

            # error handling
            if response.status_code != 200:
                ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', message=f'While getting latest version, error code {response.status_code}.'))
                return

            # get information
            latest_release = response.json()

            # get the name of the latest version
            latest_version = latest_release['name']

            # versions are different - request for update
            if latest_version != current_version:

                # ask the user if he wants to upgrade
                question = messagebox.askyesno(title="Overwatch Rank Tracker", message="Update is available.\nDo you want to update?")

                # user wants updates
                if question:

                    # run auto-update
                    subprocess.Popen(['Updater.exe'], shell=True)

                    # finishing the main process
                    sys.exit()

        # no internet connection - no update
        except requests.exceptions.ConnectionError:
            pass

        # unexpected error
        except Exception as error:
            logManager.sending_logs(api_response=response.json(), status_code=response.status_code, error=error)

        # destroy window, 2 additional methods to avoid an error in subsequent application window
        update_window.iconify()
        update_window.deiconify()
        update_window.destroy()

    def update(self):
        """Updating the program and its components."""

        try:

            # creating the main window and hiding it
            update_window = tkinter.Tk()
            update_window.withdraw()

            # get information
            latest_release_information = self.__get_information_latest_release()

            # get zip file url
            zip_file_url = self.__get_zip_file_url(latest_release_information=latest_release_information)

            # set paths
            self.__set_paths()

            # download zip file
            zip_file_content = self.__get_zip_file_content(zip_file_url=zip_file_url)
            self.__create_and_save_archive(zip_file_content=zip_file_content)

            # replacing old files with downloaded files
            self.__unpacking_archive()

            # delete archive
            os.remove(self.zip_file_path)

            # destroy window
            update_window.destroy()

        # error handling
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection error", "Internet connection problem.")
        except Exception as error:
            ThreadPoolExecutor().submit(lambda e=error: messagebox.showerror(title='Error', text=str(e)))

    def __get_information_latest_release(self):
        """Getting all the information about the latest version of this repository."""

        try:

            # request for the latest release version
            response = requests.get(f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/releases/latest")

            # error handling
            if response.status_code != 200:
                raise requests.exceptions.RequestException(f'Error when getting information about the latest version. Status code - {response.status_code}.')

            # return information
            return response.json()

        # error handling
        except Exception as error:
            raise Exception(f'Error getting information about the latest version. {error}')

    @staticmethod
    def __get_zip_file_url(latest_release_information):
        """Finding a link to download the project file."""

        for asset in latest_release_information['assets']:
            if asset['name'] == 'Overwatch.Rank.Tracker.zip':
                zip_file_url = asset['browser_download_url']
                return zip_file_url

        # error handling
        raise KeyError('Error when receiving a link to a zip file.')

    def __set_paths(self):
        """Writing paths for future unpacking of the file in the required directory."""

        self.current_folder_path = os.path.dirname(sys.argv[0])
        self.zip_file_path = os.path.join(self.current_folder_path, 'latest_release.zip')
        self.current_folder_name = os.path.basename(self.current_folder_path)

    @staticmethod
    def __get_zip_file_content(zip_file_url):
        """Downloads and returns the content of a ZIP file from the specified URL."""

        try:
            response = requests.get(zip_file_url)
            zip_content = response.content
            return zip_content

        # error handling
        except Exception as error:
            raise requests.exceptions.RequestException(f'Error when getting the contents of a zip file: {error}')

    def __create_and_save_archive(self, zip_file_content):
        """Creating and saving a ZIP file in the application directory."""

        # saving the archive in the folder with the exe file
        try:
            with open(self.zip_file_path, 'wb') as zip_file:
                zip_file.write(zip_file_content)

        # error handling
        except Exception as error:
            raise Exception(f'An error occurred when saving the archive to a folder: {error}')

    def __unpacking_archive(self):
        """Unpacking the ZIP file with replacement of everything except the file with battle tags."""

        try:
            with zipfile.ZipFile(self.zip_file_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():

                    # define file name without path
                    filename = os.path.basename(file_info.filename)

                    # extract files to the current folder without creating a subfolder
                    if filename in ["Overwatch Rank Tracker.exe", 'settings_and_battle_tags.json']:
                        if filename == 'settings_and_battle_tags.json':
                            if os.path.exists(os.path.join(self.current_folder_path, 'settings_and_battle_tags.json')):
                                continue
                        extracted_path = os.path.join(self.current_folder_path, filename)
                        with open(extracted_path, 'wb') as extracted_file:
                            extracted_file.write(zip_ref.read(file_info.filename))

            # success
            messagebox.showinfo(title="Update", message="Update downloaded successfully.")

        # error handling
        except Exception as error:
            raise Exception(f"An error occurred when unpacking the file: {error}")


if __name__ == "__main__":

    # running update
    overwatchRankTracker = OverwatchRankTracker.OverwatchRankTracker()
    updateManager = UpdateManager(owner_name=overwatchRankTracker.owner_name, repo_name=overwatchRankTracker.repo_name)
    updateManager.update()

    # launching the main application back
    subprocess.Popen(['Overwatch Rank Tracker.exe'], shell=True)
