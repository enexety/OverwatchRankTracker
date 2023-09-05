import subprocess


# run scripts
subprocess.run(['python', 'add_personal_information_to_project.py'])
subprocess.run(['python', 'build_and_archive.py'])
subprocess.run(['python', 'upload_release_asset.py'])
subprocess.run(['python', 'delete_personal_information_from_project.py'])
