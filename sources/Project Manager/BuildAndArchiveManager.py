import os
import shutil
import subprocess


class BuildAndArchiveManager:

    def __init__(self, project_directory_path):
        self.project_directory_path = project_directory_path
        self.dist_path = os.path.join(self.project_directory_path, 'dist')

    def build_project(self, zip_file_path):
        """Build project in specific paths and folders."""

        # get paths
        overwatch_rank_tracker_path = os.path.join(self.project_directory_path, 'sources', 'Overwatch Rank Tracker')
        build_path = os.path.join(self.project_directory_path, 'build')
        icon_path = os.path.join(self.project_directory_path, 'resources', 'icon.ico')
        settings_path = os.path.join(overwatch_rank_tracker_path, 'settings_and_battle_tags.json')

        # there is an old archive - delete it
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)

        # creating a folder(dist) with an exe file
        os.chdir(overwatch_rank_tracker_path)
        subprocess.run(["pyinstaller",
                        "OverwatchRankTracker.py",
                        '--distpath', self.dist_path,
                        '--specpath', self.project_directory_path,
                        '--workpath', build_path,
                        "--onefile",
                        "--noconsole",
                        "--icon", icon_path,
                        "--name", "Overwatch Rank Tracker"])
        subprocess.run(["pyinstaller",
                        "UpdateManager.py",
                        '--distpath', self.dist_path,
                        '--specpath', self.project_directory_path,
                        '--workpath', build_path,
                        "--onefile",
                        "--name", "Updater"])

        # add example settings file to dist
        shutil.copy(settings_path, self.dist_path)

        print('\nProject successfully built.')

    def archive_build(self):
        """Archiving a build with a specific design and name."""

        # get paths
        temporary_folder = os.path.join(self.project_directory_path, "Overwatch Rank Tracker")
        temporary_folder2 = os.path.join(self.project_directory_path, "Temporary Folder")

        if not os.path.exists(self.dist_path):
            raise FileNotFoundError('Error: You can not archive a build because it has not been created.')

        # duplicate a folder(dist) to get a folder with the desired name and keep the existing original folder.
        shutil.copytree(self.dist_path, temporary_folder)

        # moving the temp folder to another one so that the archive contains the folder inside
        os.makedirs(temporary_folder2)
        shutil.move(temporary_folder, temporary_folder2)

        # creating an archive from a duplicated folder
        shutil.make_archive(base_name=os.path.join(self.project_directory_path, 'Overwatch Rank Tracker'), format="zip", root_dir=temporary_folder2)

        # deleting a duplicate folder
        shutil.rmtree(temporary_folder2)

        print('\nProject build has been successfully archived.')
