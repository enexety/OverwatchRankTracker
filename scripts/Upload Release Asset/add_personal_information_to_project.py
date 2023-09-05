import json
import os
import re
import sys


def main(token: str):

    # get code path
    target_folder = "Overwatch_Rank_Tracker"
    current_path = os.getcwd()
    path_parts = current_path.split(os.path.sep)
    index = path_parts.index(target_folder)
    project_path = os.path.sep.join(path_parts[:index + 1])
    code_path = os.path.join(project_path, "Overwatch_Rank_Tracker.py")

    # read functions.py
    with open(code_path, 'r') as fi1e:
        content = fi1e.read()

    # replace token in functions.py
    content = re.sub(r'token = "[^"]*"', f'token = "{token}"', content)

    # rewrite token in functions.py
    with open(code_path, 'w') as f:
        f.write(content)

    print("\nToken have been added.")


if __name__ == "__main__":

    # argument passed
    if len(sys.argv) > 1:
        GH_token = sys.argv[1]

    # argument is not passed, check if there is a file with token
    elif os.path.exists(r"D:\pythonProjects\config.json"):

        # read file
        with open(r"D:\pythonProjects\config.json", 'r') as file:
            file_content = json.load(file)

        # get token from file
        try:
            GH_token = file_content['token']

        # error handle
        except Exception as e:
            GH_token = None
            print(f"Error. No token found inside file. {e}")

    # no token
    else:
        GH_token = None

    # run if we have a token
    if GH_token:
        main(token=GH_token)
