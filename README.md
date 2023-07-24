# Overwatch Rank Tracker

This project is a simple application built with Python and tkinter that allows you to track the rankings of Overwatch players.

It is using open API `https://overfast-api.tekrop.fr/`

## Installation

To run the application, follow these steps:

1. Clone the repository or download the source code files.
2. Open the command prompt or terminal.
3. Navigate to the project directory using the `cd` command. For example: `cd /path/to/project`.
4. Install the required dependencies by running the following command: `pip install -r requirements.txt`.

## Usage

To use the Overwatch Rank Tracker, follow these steps:

1. Run the `Overwatch_Rank_Tracker.py` file using Python.
2. The application window will open, where you can enter one or more battle-tags `example-1234` separated by commas and click the "Save" button.
3. After saving the links, the application will display the current rankings and other relevant information for each player.

## Settings

1. **Number of Requests:** You can now specify the number of simultaneous requests made to the Overwatch API. This determines how many battle-tags will be checked at the same time. Adjusting this value can affect the speed and resource usage of the application.


   Please note that setting the number of requests too high may lead to possible errors. It's recommended to keep this value at a reasonable level to avoid potential issues.

## Building with PyInstaller

To build a standalone executable file using PyInstaller, follow these steps:

1. Open the command prompt or terminal.
2. Navigate to the project directory using the `cd` command. For example: `cd /path/to/project`.
3. Run the following command:
```pyinstaller --onefile --noconsole --name "Overwatch Rank Tracker" --icon "path_to_icon\OverwatchRankTrackerDesktop_API\resources\icon.ico" --distpath "Overwath_Rank_Tracker" Overwatch_Rank_Tracker.py```

   Replace `path_to_icon` with the actual path to the icon file on your system.
4. PyInstaller will generate a standalone executable file in the "dist" directory.
5. Optionally, you can place the `settings_and_battle_tags.json` file in the same directory as the executable file to have example players battle-tags.

Enjoy!