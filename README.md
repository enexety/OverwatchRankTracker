# Overwatch Rank Tracker

Overwatch Rank Tracker is a desktop application developed using Python Tkinter. It allows you to track the rank(s) in Competitive Role Queue for one or multiple accounts for PC players.

Additionally, the application displays essential player statistics, including season data, playtime, win rate, and KD.

The displayed information will only be shown if the account is not set to private and the player has participated in Competitive Role Queue at least once. Otherwise, the status will be indicated as Private/Limited.

In the Season column, the player's latest competitive season will be shown, while all other statistics will be relevant to that specific season.

This application uses an open **[API](https://overfast-api.tekrop.fr/)**


## Installation


* **[Windows](https://github.com/enexety/Overwath_Rank_Tracker_API/releases)**


## Screenshots


<p align="center">
  <img src="https://github.com/enexety/Overwath_Rank_Tracker/assets/110674990/2c138968-15b2-433c-b2b1-e70a997431bb" width="410">
  <img src="https://github.com/enexety/Overwath_Rank_Tracker/assets/110674990/32d1c9c6-8be9-43ac-9bff-5ab6772b44d5" width="410">
</p>


## Usage

1. Run the `Overwatch_Rank_Tracker.exe`.
2. The application window will be open, where you can enter one or more battle-tags separated by commas: `example-1234, anotherone-5678`.
3. You can press the 'Check' button to view the rating of tracked players.


## Settings

1. **Number of Requests:** You can specify the number of simultaneous requests made to the Overwatch API. This determines how many battle-tags will be checked at the same time. Adjusting this value can affect the speed and resource usage of the application.

Please note that setting the number of requests too high may lead to possible errors. It's recommended to keep this value at a reasonable level to avoid potential issues.

Enjoy!
