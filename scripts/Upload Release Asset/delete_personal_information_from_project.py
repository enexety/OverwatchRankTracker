import sys


def main(username: str, token: str):

    # paths
    upload_path = r"D:\pythonProjects\Overwatch_Rank_Tracker\scripts\Upload Release Asset\upload_release_asset.py"
    functions_path = r"D:\pythonProjects\Overwatch_Rank_Tracker\functions.py"

    # read and replace personal data in functions.py
    with open(functions_path, 'r') as file:
        content = file.read()
    content = content.replace(f'username = "{username}"', 'username = ""')
    content = content.replace(f'token = "{token}"', 'token = ""')

    # rewrite personal data in functions.py
    with open(functions_path, 'w') as file:
        file.write(content)

    # read and replace personal data in upload_release_asset.py
    with open(upload_path, 'r') as file:
        content = file.read()
    content = content.replace(f'token = "{token}"', 'token = ""')

    # rewrite personal data in upload_release_asset.py
    with open(upload_path, 'w') as file:
        file.write(content)

    print("Token and name have been removed.")


if __name__ == "__main__":
    GH_username = sys.argv[1] if len(sys.argv) > 1 else ''
    GH_token = sys.argv[2] if len(sys.argv) > 2 else ''

    main(username=str(GH_username), token=str(GH_token))
