import os
import subprocess
import time

import keyboard
import requests
import shutil


def create_zip_file(zip_file_path, dist_path, project_folder_name, temporary_folder):
    """Creates a zip file with an exe file for release"""

    # there is an old archive - delete it
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)

    # duplicate a folder(dist) to get a folder with the desired name and keep the existing original folder.
    shutil.copytree(dist_path, project_folder_name)

    # creating an archive from a duplicated folder
    shutil.make_archive(temporary_folder, "zip")

    # deleting a duplicate folder
    shutil.rmtree(temporary_folder)

    print("Zip file created.")


def get_new_tag(owner, repo, headers):
    """Gets the last tag and increments it"""

    url = f"https://api.github.com/repos/{owner}/{repo}/tags"
    response_get_last_tag = requests.get(url=url, headers=headers)

    # error handling
    if response_get_last_tag.status_code != 200:
        raise Exception(f"Error while getting tag, error code {response_get_last_tag.status_code}.")

    tags = response_get_last_tag.json()
    latest_tag = tags[0]['name']
    tag = latest_tag[1:]
    parts = tag.split('.')
    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])
    if patch < 9:
        patch += 1
    elif minor < 9:
        minor += 1
        patch = 0
    else:
        major += 1
        minor = 0
        patch = 0
    new_tag = f"v{major}.{minor}.{patch}"

    print("\nNew tag generated.")

    return new_tag


def generate_release_description(tag: str):
    """Takes the message of the last commit and edits it to fit the Release description"""

    # getting the name of the last commit
    command = ["git", "log", "-1", "--pretty=format:%s"]
    last_commit_message = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip().split(". ")

    # changing the last commit to fit the description format
    description = "\n".join(f"> * {change.strip('.')}." for change in last_commit_message)
    description = f"> **{tag}**:\n>\n{description}\n>\n> Download below"

    print("Generated release description.")

    return description


def create_release(owner, repo, tag, headers):
    """Creates a release"""

    data = {"owner": owner, "repo": repo, "tag_name": tag}
    create_release_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    response = requests.post(url=create_release_url, json=data, headers=headers)
    release_id = response.json()["id"]

    # error handling
    if response.status_code != 201:
        delete_release_and_tag(tag=tag, owner=owner, release_id=release_id, headers=headers, repo=repo)
        raise Exception(f"Error when creating a release, error code {response.status_code}.")

    upload_url = response.json()["upload_url"]

    print("Release has been created.")

    return upload_url, release_id


def describe_release(tag, owner, repo, release_id, headers):
    """Creates a description of the release"""

    update_data = {"body": generate_release_description(tag=tag)}
    update_release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/{release_id}"
    response = requests.patch(update_release_url, json=update_data, headers=headers)

    if response.status_code != 200:
        delete_release_and_tag(tag=tag, owner=owner, release_id=release_id, headers=headers, repo=repo)
        raise Exception(f"Error when creating release description, error code {response.status_code}.")

    print("Changed release description.")


def change_release_name(tag, headers, owner, repo, release_id):
    """Creates a title for the release"""

    edit_release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/{release_id}"
    data = {"name": tag}
    response = requests.patch(edit_release_url, json=data, headers=headers)

    if response.status_code != 200:
        delete_release_and_tag(tag=tag, owner=owner, release_id=release_id, headers=headers, repo=repo)
        raise Exception(f"Error when changing the release name, error code {response.status_code}.")

    print("Changed title of the release.")


def upload_zip_to_release(zip_file_path, headers, upload_url, tag, owner, release_id, repo):
    """Uploads a zip file to the release"""

    with open(zip_file_path, 'rb') as zip_file:
        upload_url = upload_url.replace("{?name,label}", f"?name=Overwatch Rank Tracker.zip")  # noqa: F541
        response = requests.post(upload_url, headers=headers, data=zip_file.read())

    if response.status_code != 201:
        delete_release_and_tag(tag=tag, owner=owner, release_id=release_id, headers=headers, repo=repo)
        raise Exception(f"Error when changing the release name, error code {response.status_code}.")

    print("Zip file uploaded.")


def delete_release_and_tag(tag, owner, repo, release_id, headers):
    """Deletes the release"""

    # delete release
    delete_release_url = f"https://api.github.com/repos/{owner}/{repo}/releases/{release_id}"
    response_delete_release = requests.delete(delete_release_url, headers=headers)

    # error handling
    if response_delete_release.status_code != 204:
        raise Exception(f"Failed to delete release, error code {response_delete_release.status_code}.")

    # delete tag
    delete_tag_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/tags/{tag}"
    response_delete_tag = requests.delete(delete_tag_url, headers=headers)

    # error handling
    if response_delete_tag.status_code != 204:
        raise Exception(f"Failed to delete tag, error code {response_delete_tag.status_code}.")

    print("Release and tag has been removed")


class UploadReleaseAsset:

    # creating a folder(dist) with an exe file
    os.chdir(r"D:\pythonProjects\Overwatch_Rank_Tracker")
    subprocess.run(["pyinstaller", "Overwatch Rank Tracker.spec"])

    # personal information
    github_token = ""

    # variables
    owner = 'enexety'
    repo = 'Overwatch_Rank_Tracker'
    headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/zip"}
    project_folder_name = "Overwatch Rank Tracker"
    new_tag = get_new_tag(owner=owner, repo=repo, headers=headers)

    # paths
    project_path = os.getcwd()
    zip_file_path = os.path.join(project_path, "Overwatch Rank Tracker.zip")
    dist_path = os.path.join(project_path, "dist")
    temporary_folder = os.path.join(project_path, project_folder_name)

    # processes
    try:
        create_zip_file(zip_file_path=zip_file_path, dist_path=dist_path, project_folder_name=project_folder_name, temporary_folder=temporary_folder)
        upload_url, release_id = create_release(owner=owner, repo=repo, headers=headers, tag=new_tag)
        change_release_name(tag=new_tag, headers=headers, owner=owner, repo=repo, release_id=release_id)
        describe_release(tag=new_tag, owner=owner, repo=repo, release_id=release_id, headers=headers)
        upload_zip_to_release(zip_file_path=zip_file_path, headers=headers, upload_url=upload_url, repo=repo, tag=new_tag, release_id=release_id, owner=owner)

    # time to see what's wrong
    except Exception as e:
        print(f"\nError. {e}Press any button to finish...")
        keyboard.read_event()

    # code passed successfully
    else:
        print("\nCode was executed successfully.\n")
        seconds = 5
        for i in range(seconds, 0, -1):
            print(f"Window closes after {seconds} seconds.")
            seconds -= 1
            time.sleep(1)
