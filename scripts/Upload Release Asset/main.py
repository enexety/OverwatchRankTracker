import subprocess

username = ''
token = ''

subprocess.run(['python', 'add_personal_information_to_project.py', username, token])
subprocess.run(['python', 'upload_release_asset.py'])
subprocess.run(['python', 'delete_personal_information_from_project.py', username, token])
