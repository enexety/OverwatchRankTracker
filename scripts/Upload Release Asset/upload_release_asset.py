import os
import subprocess
import requests

from Overwatch_Rank_Tracker import token, owner_name, repo_name
from build_and_archive import zip_file_path, project_path


# change directory to project path
os.chdir(project_path)


def get_new_tag(headers):
    """Gets the last tag and increments it"""

    url = f"https://api.github.com/repos/{owner_name}/{repo_name}/tags"
    response_get_latest_tag = requests.get(url=url, headers=headers)

    # error handling
    if response_get_latest_tag.status_code != 200:
        raise Exception(f"Error while getting tag, error code {response_get_latest_tag.status_code}.")

    tags = response_get_latest_tag.json()
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


def create_release(tag, headers, release_description: str):
    """Creates a release"""

    # get latest release description
    response = requests.get(f"https://api.github.com/repos/{owner_name}/{repo_name}/releases/latest")
    latest_release_description = response.json()["body"]

    # comparing releases without the first line
    if latest_release_description.strip().split('\n')[1:] == release_description.strip().split('\n')[1:]:
        raise Exception("Error when creating a release. Such a release already exists. The title of the release is the same as the previous one.")

    data = {"owner": owner_name, "repo": repo_name, "tag_name": tag}
    create_release_url = f"https://api.github.com/repos/{owner_name}/{repo_name}/releases"
    response = requests.post(url=create_release_url, json=data, headers=headers)
    release_id = response.json()["id"]

    # error handling
    if response.status_code != 201:
        delete_release_and_tag(tag=tag, release_id=release_id, headers=headers)
        raise Exception(f"Error when creating a release, error code {response.status_code}.")

    upload_url = response.json()["upload_url"]

    print("Release has been created.")

    return upload_url, release_id


def describe_release(tag, release_id, headers, release_description):
    """Creates a description of the release"""

    update_data = {"body": release_description}
    update_release_url = f"https://api.github.com/repos/{owner_name}/{repo_name}/releases/{release_id}"
    response = requests.patch(update_release_url, json=update_data, headers=headers)

    if response.status_code != 200:
        delete_release_and_tag(tag=tag, release_id=release_id, headers=headers)
        raise Exception(f"Error when creating release description, error code {response.status_code}.")

    print("Changed release description.")


def change_release_name(tag, headers, release_id):
    """Creates a title for the release"""

    edit_release_url = f"https://api.github.com/repos/{owner_name}/{repo_name}/releases/{release_id}"
    data = {"name": tag}
    response = requests.patch(edit_release_url, json=data, headers=headers)

    if response.status_code != 200:
        delete_release_and_tag(tag=tag, release_id=release_id, headers=headers)
        raise Exception(f"Error when changing the release name, error code {response.status_code}.")

    print("Changed title of the release.")


def upload_zip_to_release(headers, upload_url, tag, release_id):
    """Uploads a zip file to the release"""

    with open(zip_file_path, 'rb') as zip_file:
        upload_url = upload_url.replace("{?name,label}", f"?name=Overwatch Rank Tracker.zip")  # noqa: F541
        response = requests.post(upload_url, headers=headers, data=zip_file.read())

    if response.status_code != 201:
        delete_release_and_tag(tag=tag, release_id=release_id, headers=headers)
        raise Exception(f"Error when changing the release name, error code {response.status_code}.")

    print("Zip file uploaded.")


def delete_release_and_tag(tag, release_id, headers):
    """Deletes the release"""

    # delete release
    delete_release_url = f"https://api.github.com/repos/{owner_name}/{repo_name}/releases/{release_id}"
    response_delete_release = requests.delete(delete_release_url, headers=headers)

    # error handling
    if response_delete_release.status_code != 204:
        raise Exception(f"Failed to delete release, error code {response_delete_release.status_code}.")

    # delete tag
    delete_tag_url = f"https://api.github.com/repos/{owner_name}/{repo_name}/git/refs/tags/{tag}"
    response_delete_tag = requests.delete(delete_tag_url, headers=headers)

    # error handling
    if response_delete_tag.status_code != 204:
        raise Exception(f"Failed to delete tag, error code {response_delete_tag.status_code}.")

    print("Release and tag has been removed")


def main():

    # variables
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/zip"}
    new_tag = get_new_tag(headers=headers)
    release_description = generate_release_description(tag=new_tag)

    # processes
    try:
        upload_url, release_id = create_release(headers=headers, tag=new_tag, release_description=release_description)
        change_release_name(tag=new_tag, headers=headers, release_id=release_id)
        describe_release(tag=new_tag, release_id=release_id, headers=headers, release_description=release_description)
        upload_zip_to_release(headers=headers, upload_url=upload_url, tag=new_tag, release_id=release_id)

    # error handle, time to see what is wrong
    except Exception as e:
        print(f"\nError. {e}")


if __name__ == "__main__":
    main()
