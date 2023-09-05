import os
import shutil
import subprocess


# get the path to "Overwatch_Rank_Tracker"
target_folder = "Overwatch_Rank_Tracker"
current_path = os.getcwd()
path_parts = current_path.split(os.path.sep)
index = path_parts.index(target_folder)

# paths
project_path = os.path.sep.join(path_parts[:index + 1])
zip_file_path = os.path.join(project_path, "Overwatch Rank Tracker.zip")
dist_path = os.path.join(project_path, "dist")
temporary_folder = os.path.join(project_path, "Overwatch Rank Tracker")
temporary_folder2 = os.path.join(project_path, "Temporary Folder")
icon_path = os.path.join(project_path, r"resources\icon.ico")
settings_path = os.path.join(project_path, "settings_and_battle_tags.json")


def main():

    # creating a folder(dist) with an exe file
    os.chdir(project_path)
    subprocess.run(["pyinstaller", "Overwatch_Rank_Tracker.py", "--onefile", "--noconsole", "--icon", icon_path, "--name", "Overwatch Rank Tracker"])
    subprocess.run(["pyinstaller", "Updater.py", "--onefile", "--name", "Updater"])

    # add example settings file to dist
    if not os.path.exists(os.path.join(dist_path, "settings_and_battle_tags.json")):
        shutil.copy(settings_path, dist_path)

    print('\nFolder with exe file has been created.')

    # there is an old archive - delete it
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)

    # duplicate a folder(dist) to get a folder with the desired name and keep the existing original folder.
    shutil.copytree(dist_path, temporary_folder)

    # moving the temp folder to another one so that the archive contains the folder inside
    os.makedirs(temporary_folder2)
    shutil.move(temporary_folder, temporary_folder2)

    # creating an archive from a duplicated folder
    shutil.make_archive("Overwatch Rank Tracker", "zip", temporary_folder2)

    # deleting a duplicate folder
    shutil.rmtree(temporary_folder2)

    print("Zip file created.")


if __name__ == "__main__":
    main()
