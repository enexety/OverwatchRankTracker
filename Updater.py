import os
import subprocess
import zipfile
from tkinter import messagebox
import requests
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk

from Overwatch_Rank_Tracker import OverwatchRankTracker


def main():

    # creating the main window and hiding it
    window = tk.Tk()
    window.withdraw()

    try:

        # request for the latest release version
        response = requests.get(f"https://api.github.com/repos/{OverwatchRankTracker.owner_name}/{OverwatchRankTracker.repo_name}/releases/latest")

    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection error", "Internet connection problem.")
        return

    # error handling
    if response.status_code != 200:
        ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', text=f'While getting latest version, error code {response.status_code}.'))
        return

    # get information
    latest_release = response.json()

    # get link to download zip file
    zip_file_url = None
    for asset in latest_release['assets']:
        if asset['name'] == 'Overwatch.Rank.Tracker.zip':
            zip_file_url = asset['browser_download_url']
            break

    # link received successfully
    if zip_file_url:

        # folders paths
        current_folder_path = os.getcwd()
        parent_folder_path = os.path.abspath(os.path.join(current_folder_path, os.pardir))
        zip_file_path = os.path.join(current_folder_path, 'latest_release.zip')
        current_folder_name = os.path.basename(current_folder_path)

        # download zip
        try:
            response = requests.get(zip_file_url)
            zip_content = response.content
        except Exception as e:
            messagebox.showerror(title="Error", message=f"An error occurred when downloading the file: {e}")
            return

        # saving the archive in the folder with the exe file
        try:
            with open(zip_file_path, 'wb') as zip_file:
                zip_file.write(zip_content)
        except Exception as e:
            messagebox.showerror(title="Error", message=f"An error occurred when saving the archive to a folder: {e}")
            return

        # unpacking the archive
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename not in [f'{current_folder_name}/settings_and_battle_tags.json', f'{current_folder_name}/Updater.exe']:
                        zip_ref.extract(file_info.filename, parent_folder_path)

            # success
            messagebox.showinfo(title="Update", message="Update downloaded successfully.")

        # error handling
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred when unpacking the file: {e}")

        # deleting an archive
        os.remove(zip_file_path)

    # error handling
    else:
        messagebox.showerror(title="Update Error", message="Could not find url of the zip file.")


if __name__ == "__main__":
    main()
    subprocess.run(['python', 'Overwatch Rank Tracker.exe'])
