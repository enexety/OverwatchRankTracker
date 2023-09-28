import subprocess
import requests


class UploadReleaseAsset:

    def __init__(self, owner_name, repo_name, zip_file_path, token):
        self.owner_name = owner_name
        self.repo_name = repo_name
        self.token = token
        self.zip_file_path = zip_file_path

        self.headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/zip"}
        self.tag = self.__get_new_tag()

    def __get_new_tag(self):
        """Gets the last tag and increments it."""

        url = f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/tags"
        response_get_latest_tag = requests.get(url=url, headers=self.headers)

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

    def __generate_release_description(self):
        """Takes the message of the last commit and edits it to fit the Release description."""

        # getting the name of the last commit
        command = ["git", "log", "-1", "--pretty=format:%s"]
        last_commit_message = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip().split(". ")

        # changing the last commit to fit the description format
        description = "\n".join(f"> * {change.strip('.')}." for change in last_commit_message)
        description = f"> **{self.tag}**:\n>\n{description}\n>\n> Download below"

        print("Generated release description.")

        return description

    def __create_release(self, release_description: str):
        """Creates a release."""

        # get latest release description
        response = requests.get(f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/releases/latest")
        latest_release_description = response.json()["body"]

        # comparing releases without the first line
        if latest_release_description.strip().split('\n')[1:] == release_description.strip().split('\n')[1:]:
            raise Exception("Error when creating a release. Such a release already exists. The title of the release is the same as the previous one.")

        data = {"owner": self.owner_name, "repo": self.repo_name, "tag_name": self.tag}
        create_release_url = f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/releases"
        response = requests.post(url=create_release_url, json=data, headers=self.headers)
        release_id = response.json()["id"]

        # error handling
        if response.status_code != 201:
            self.__delete_release_and_tag(release_id=release_id)
            raise Exception(f"Error when creating a release, error code {response.status_code}.")

        upload_url = response.json()["upload_url"]

        print("Release has been created.")

        return upload_url, release_id

    def __describe_release(self, release_id, release_description):
        """Creates a description of the release."""

        update_data = {"body": release_description}
        update_release_url = f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/releases/{release_id}"
        response = requests.patch(update_release_url, json=update_data, headers=self.headers)

        if response.status_code != 200:
            self.__delete_release_and_tag(release_id=release_id)
            raise Exception(f"Error when creating release description, error code {response.status_code}.")

        print("Changed release description.")

    def __change_release_name(self, release_id):
        """Creates a title for the release."""

        edit_release_url = f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/releases/{release_id}"
        data = {"name": self.tag}
        response = requests.patch(edit_release_url, json=data, headers=self.headers)

        if response.status_code != 200:
            self.__delete_release_and_tag(release_id=release_id)
            raise Exception(f"Error when changing the release name, error code {response.status_code}.")

        print("Changed title of the release.")

    def __upload_zip_to_release(self, upload_url, release_id):
        """Uploads a zip file to the release."""

        with open(self.zip_file_path, 'rb') as zip_file:
            upload_url = upload_url.replace("{?name,label}", f"?name=Overwatch Rank Tracker.zip")  # noqa: F541
            response = requests.post(upload_url, headers=self.headers, data=zip_file.read())

        if response.status_code != 201:
            self.__delete_release_and_tag(release_id=release_id)
            raise Exception(f"Error when changing the release name, error code {response.status_code}.")

        print("Zip file uploaded.")

    def __delete_release_and_tag(self, release_id):
        """Deletes the release."""

        # delete release
        delete_release_url = f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/releases/{release_id}"
        response_delete_release = requests.delete(delete_release_url, headers=self.headers)

        # error handling
        if response_delete_release.status_code != 204:
            raise Exception(f"Failed to delete release, error code {response_delete_release.status_code}.")

        # delete tag
        delete_tag_url = f"https://api.github.com/repos/{self.owner_name}/{self.repo_name}/git/refs/tags/{self.tag}"
        response_delete_tag = requests.delete(delete_tag_url, headers=self.headers)

        # error handling
        if response_delete_tag.status_code != 204:
            raise Exception(f"Failed to delete tag, error code {response_delete_tag.status_code}.")

        print("Release and tag has been removed.")

    def run(self):
        """Sequentially run functions to perform the process of creating, describing,
        and loading a release of the current version of the application. It uses a local zip file created earlier in other functions or manually."""

        # variables
        release_description = self.__generate_release_description()

        # processes
        try:
            upload_url, release_id = self.__create_release(release_description=release_description)
            self.__change_release_name(release_id=release_id)
            self.__describe_release(release_id=release_id, release_description=release_description)
            self.__upload_zip_to_release(upload_url=upload_url, release_id=release_id)

        # handling of unpredictable errors
        except Exception as e:
            print(f"\nError. {e}")
