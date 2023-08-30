import os
import re


def main():

    # get code path
    target_folder = "Overwatch_Rank_Tracker"
    current_path = os.getcwd()
    path_parts = current_path.split(os.path.sep)
    index = path_parts.index(target_folder)
    project_path = os.path.sep.join(path_parts[:index + 1])
    code_path = os.path.join(project_path, "Overwatch_Rank_Tracker.py")

    # read and replace personal data in functions.py
    with open(code_path, 'r') as file:
        content = file.read()

    content = re.sub(r'token = "[^"]*"', 'token = ""', content)

    # rewrite personal data in functions.py
    with open(code_path, 'w') as file:
        file.write(content)

    print("\nToken have been removed.")


if __name__ == "__main__":
    main()
