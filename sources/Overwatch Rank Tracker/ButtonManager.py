import os
import signal
import sys
import tkinter
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox, Button, ttk, Text
import concurrent
import requests


class ButtonManager:

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.button_frame = None
        self.user_want_stop = False
        self.public_profiles = []
        self.limited_profiles = []
        self.private_profiles = []
        self.error_battle_tags = []

    def set_button_frame(self):
        """Creates a frame for the buttons."""

        self.button_frame = tkinter.Frame(self.mainWindow.main_window, bg='#2B2B2B')
        self.button_frame.pack(side='bottom', fill='x')

    def set_buttons(self):
        """Creates buttons and assigns commands to them."""

        check_button = tkinter.Button(self.button_frame, text='Check', font=('Calibri', 17, 'bold'), pady=3, width=16,
                                      command=lambda: ThreadPoolExecutor().submit(lambda: self.__check_button_click(check_button=check_button, save_button=save_button)))
        save_button = tkinter.Button(self.button_frame, text='Save', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: self.__save_button_click())
        settings_button = tkinter.Button(self.button_frame, text='Settings', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: self.__click_settings_button())
        exit_button = tkinter.Button(self.button_frame, text='Exit', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: self.click_exit_button())
        check_button.pack(side='left', fill='x', expand=True)
        save_button.pack(side='left', fill='x', expand=True)
        settings_button.pack(side='left', fill='x', expand=True)
        exit_button.pack(side='left', fill='x', expand=True)

    def click_exit_button(self):
        """Prompts to save unsaved data and terminates the application completely."""

        # get battle-tags from file
        battle_tags_file = self.mainWindow.fileManager.read_file().get("Battle-tags", [])

        # current widget - text widget, get current content
        if type(self.mainWindow.widgetManager.current_widget) is Text:
            self.mainWindow.widgetManager.text_widget_content = self.mainWindow.widgetManager.current_widget.get("1.0", tkinter.END).strip()

        # content adjustment, split data by commas, remove extra spaces in each battle-tag
        text_widget_content = [tag.strip() for tag in self.mainWindow.widgetManager.text_widget_content.split(",")]

        # question: save text or not if text-widget content and file content different
        if set(battle_tags_file) != set(text_widget_content):
            if messagebox.askquestion(title='Exit', message='Are you want to save your battle-tags list?') == 'yes':
                self.__save_button_click()

        # close
        os.kill(os.getpid(), signal.SIGTERM)

    def __click_settings_button(self):
        """Opens a window with settings."""

        # set window-setting
        settings_window = tkinter.Toplevel(self.mainWindow.main_window)
        settings_window.title("Settings")
        settings_window.resizable(False, False)  # prevent window resizing
        settings_window.attributes('-topmost', True)  # window on top
        settings_window.grab_set()  # make the settings window modal (blocks access to other windows while the window is open)
        settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)  # custom close
        settings_window_height = 120
        settings_window_width = 190
        self.mainWindow.center_window(window=settings_window, window_width=settings_window_width, window_height=settings_window_height)

        # empty cell for top indent
        empty_label_top = tkinter.Label(settings_window)
        empty_label_top.grid(row=0, column=0)

        # "Number of requests" text
        label = tkinter.Label(settings_window, text="Number of requests")
        label.grid(row=1, column=0, padx=5)

        # "Number of requests" field for entering number
        num_requests_var = tkinter.StringVar(value=str(self.mainWindow.fileManager.max_workers))
        entry = tkinter.Spinbox(settings_window, from_=1, to=6, textvariable=num_requests_var, width=5)
        entry.grid(row=1, column=1, padx=5)

        # button save
        x_button = settings_window_width // 2
        y_button = settings_window_height - 30
        setting_save_button = ttk.Button(settings_window, text="Save", width=8, command=lambda: __settings_save_click())
        setting_save_button.place(x=x_button, y=y_button, anchor='center')

        # top right buttons style
        settings_window.wm_attributes("-toolwindow", 1) if tkinter.TkVersion >= 8.5 and sys.platform.startswith('win') else None

        def __settings_save_click():
            """Saves the changed settings."""

            # change max_workers value
            self.mainWindow.fileManager.max_workers = int(num_requests_var.get())

            self.mainWindow.fileManager.overwriting_file(max_workers_bool=True)
            settings_window.destroy()

    def __save_button_click(self):
        """Save battle-tags from text-widget."""

        # get data from text-widget
        data = self.mainWindow.widgetManager.current_widget.get('1.0', tkinter.END).strip()

        # split data by commas, remove extra spaces in each battle-tag
        new_battle_tags = [tag.strip() for tag in data.split(",")]

        # rewrite file with new datas
        self.mainWindow.fileManager.overwriting_file(battle_tags_bool=True, battle_tags=new_battle_tags)

    def __battle_tags_button_click(self, save_button: Button):
        """Open text-widget, change "Link" button to "Save" button."""

        # flag for stop check
        self.user_want_stop = True

        # remove table-widget
        self.mainWindow.widgetManager.destroy_widget()

        # create text-widget
        self.mainWindow.widgetManager.create_text_widget(fileManager=self.mainWindow.fileManager)

        # change button
        save_button.configure(text='Save', command=lambda: self.__save_button_click())

    def __check_button_click(self, check_button: Button, save_button: Button):
        """Performs a series of actions to retrieve information about each user entered in the text widget field."""

        # to avoid problems in further clicks
        self.user_want_stop = False
        self.error_battle_tags.clear()
        self.private_profiles.clear()
        self.public_profiles.clear()
        self.limited_profiles.clear()

        # block button
        check_button.configure(state='disabled')

        try:

            # for text-widget
            if type(self.mainWindow.widgetManager.current_widget) is Text:

                # change "save" button to "battle-tags" button
                save_button.configure(text='Battle-tags', command=lambda: self.__battle_tags_button_click(save_button=save_button))

                # get information from text widget
                self.mainWindow.widgetManager.text_widget_content = self.mainWindow.widgetManager.current_widget.get('1.0', tkinter.END).strip()

            # information in text-widget is available
            if self.mainWindow.widgetManager.text_widget_content:

                # battle-tags list
                battle_tags = [tag.strip() for tag in self.mainWindow.widgetManager.text_widget_content.split(",")]

                # delete text or table widget
                if not self.user_want_stop and type(self.mainWindow.widgetManager.current_widget) is Text or ttk.Treeview:
                    self.mainWindow.widgetManager.destroy_widget()

                    # push information on table
                    try:
                        self.__get_content_and_push(battle_tags=battle_tags)

                    # no internet connection - to bring it all back and give an error
                    except requests.exceptions.ConnectionError:

                        # revert the text widget back
                        self.mainWindow.widgetManager.create_text_widget(fileManager=self.mainWindow.fileManager)

                        # change button back
                        save_button.configure(text='Save', command=lambda: self.__save_button_click())

                        # message error
                        messagebox.showerror("Connection Error", "Internet connection problem.")

            # no battle-tags - raise error
            else:
                raise ValueError

        # error window - no battle tags
        except ValueError:

            # to put "save" button back on
            save_button.configure(text='Save', command=lambda: self.__save_button_click())

            ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', message='List of battle tags is empty.'))

        # error window if battle-tag(s) was not found
        if len(self.error_battle_tags) > 0:
            ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', message=f'This account(s): ({", ".join(map(str, self.error_battle_tags))}) was not found.'))

        # unblock button
        check_button.configure(state='normal')

        # reset flag
        self.user_want_stop = False

    def __get_content_and_push(self, battle_tags: list):
        """Getting the information for each of the battle-tags and adding this to table-widget in the correct order."""

        # not to create more than one identical error window
        error_occurred = False

        # multithreaded request retrieval
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.mainWindow.fileManager.max_workers) as executor:
            futures = [executor.submit(self.__process_and_sort_account, battle_tag) for battle_tag in battle_tags]

            if self.user_want_stop:
                return

            # handle exceptions if any occur during the execution of threads
            for future, battle_tag in zip(futures, battle_tags):
                try:
                    future.result()

                # no internet connect
                except requests.exceptions.ConnectionError:
                    raise requests.exceptions.ConnectionError

                # error handling
                except requests.RequestException:

                    # one error-window no more
                    if not error_occurred:
                        error_occurred = True
                        ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', message='Too many requests: Reduce the number of requests in the settings.\n'
                                                                                                        'If it does not help, there may be a problem:\n\n'
                                                                                                        '1. Problem in the server.\n'
                                                                                                        '2. Check if you added the battle tags correctly.\n'))

        if self.user_want_stop:
            return

        self.mainWindow.widgetManager.create_table_widget()

        # push content in the right order
        for unit in self.public_profiles:
            if self.user_want_stop:
                return
            self.mainWindow.widgetManager.current_widget.insert('', tkinter.END, values=unit, tags=['Public'])
        for unit in self.limited_profiles:
            if self.user_want_stop:
                return
            self.mainWindow.widgetManager.current_widget.insert('', tkinter.END, values=unit, tags=['Limited'])
        for unit in self.private_profiles:
            if self.user_want_stop:
                return
            self.mainWindow.widgetManager.current_widget.insert('', tkinter.END, values=unit, tags=['Private'])

    def __process_and_sort_account(self, one_battle_tag: str):
        """Sort an account by status into a separate list."""

        information = self.__get_and_process_single_account_info(battle_tag=one_battle_tag)

        # if needed exit
        if self.user_want_stop:
            return

        # record 3 different types to the relevant lists
        if information:
            if information[0] == 'Public':
                self.public_profiles.append(information)
            elif information[0] == 'Limited':
                self.limited_profiles.append(information)
            else:
                self.private_profiles.append(information)

    def __get_and_process_single_account_info(self, battle_tag: str):
        """Getting information from API on one account and then processing it."""

        # variables
        tank_rating = '-'
        damage_rating = '-'
        support_rating = '-'
        time_played = '-'
        win_rate = '-'
        kd = '-'
        season = '-'

        if self.user_want_stop:
            return

        # get content from API
        response = requests.get(f'https://overfast-api.tekrop.fr/players/{battle_tag}')
        status_code = response.status_code
        response = response.json()

        # record and return data
        try:

            # wrong battle-tag
            if "-" not in battle_tag:
                raise KeyError

            nickname = battle_tag.split("-")[0] + '#' + battle_tag.split("-")[1]
            status = str(response['summary']['privacy']).capitalize()
            if status == 'Public':

                if type(response['summary']['competitive']) is dict:  # this return "None" if no competitive
                    try:

                        # stats
                        season = response['summary']['competitive']['pc']['season']
                        stats = response['stats']['pc']['competitive']['career_stats']['all-heroes']
                        eliminations = next((stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'eliminations'), 0)
                        deaths = next((stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'deaths'), 0)
                        sec_played = next((stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'time_played'), 0)
                        games_played = next((stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_played'), 0)
                        games_won = next((stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_won'), 0)

                        # stats calculation
                        time_played = f'{sec_played // 3600}hr {(sec_played % 3600) // 60}min'
                        win_rate = f"{(games_won / games_played) * 100:.2f}%"
                        kd = f'{eliminations / deaths:.2f}'

                        # tank rating
                        if type(response['summary']['competitive']['pc']['tank']) is dict:
                            tank_division = str(response['summary']['competitive']['pc']['tank']['division']).capitalize()
                            tank_division_tier = str(response['summary']['competitive']['pc']['tank']['tier'])
                            tank_rating = tank_division + '-' + tank_division_tier

                        if self.user_want_stop:
                            return

                        # damage rating
                        if type(response['summary']['competitive']['pc']['damage']) is dict:
                            damage_division = str(response['summary']['competitive']['pc']['damage']['division']).capitalize()
                            damage_division_tier = str(response['summary']['competitive']['pc']['damage']['tier'])
                            damage_rating = damage_division + '-' + damage_division_tier

                        # support rating
                        if type(response['summary']['competitive']['pc']['support']) is dict:
                            support_division = str(response['summary']['competitive']['pc']['support']['division']).capitalize()
                            support_division_tier = str(response['summary']['competitive']['pc']['support']['tier'])
                            support_rating = support_division + '-' + support_division_tier

                        return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

                    # unexpected error
                    except Exception as error:
                        if self.user_want_stop:
                            return

                        # send logs
                        self.mainWindow.logManager.sending_logs(api_response=response, status_code=status_code, error=error)

                        # error window
                        ThreadPoolExecutor().submit(lambda e=error: messagebox.showerror(title=f'{battle_tag}', message=f'Sorry, something went wrong. {e}'))

                # no competitive
                else:
                    status = 'Limited'
                    return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

            # profile is closed
            else:
                return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

        # it happens when could not get blizzard page
        except KeyError:
            if self.user_want_stop is not True:

                # add a battle-tag to further output a single error with multiple or single battle-tags
                self.error_battle_tags.append(battle_tag)

            return
