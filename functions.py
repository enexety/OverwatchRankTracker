import concurrent
import os
import signal
from tkinter import ttk, messagebox
import tkinter as tk
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import sys

# create global variables
public_profiles = []
limited_profiles = []
private_profiles = []
user_want_stop = False
widget_info = None

# initial settings
max_workers = 6


def read_file(path: str):
    """Returns the contents of a file"""
    with open(path, 'r') as file:
        return json.load(file)


def write_file(path: str, paste):
    """Record file with new content"""
    with open(path, 'w') as file:
        json.dump(paste, file, indent=2)


def overwriting_file(path: str, max_workers_bool: bool = False, battle_tags_bool: bool = False, battle_tags=None, full_rewrite: bool = False):
    """Overwrite file or certain blocks in file"""

    if battle_tags is None:
        battle_tags = []

    # file exists
    try:

        # call error for rewrite file
        if full_rewrite:
            raise FileNotFoundError

        # read file and rewrite certain settings
        file_content = read_file(path=path)
        if max_workers_bool:
            file_content["Settings"]["max_workers"] = int(max_workers)
        if battle_tags_bool:
            file_content["Battle-tags"] = battle_tags
        if max_workers_bool or battle_tags_bool:
            write_file(paste=file_content, path=path)

    # file do not exist
    except FileNotFoundError:
        write_file(path=path, paste={"Settings": {"max_workers": int(max_workers)}, "Battle-tags": battle_tags})


def create_scrollbar(frame, widget):
    """It creates scrollbar"""
    scrollbar = ttk.Scrollbar(frame, command=widget.yview)
    scrollbar.pack(side='right', fill='y', pady=10)
    widget.config(yscrollcommand=scrollbar.set)


def create_table_widget(table):
    """Create table-widget, columns = 9
       for 800x600, full length = 796
       if you set the minimum length for all columns, full length = 598"""

    # delete information from the table if it exists
    if table.get_children():
        table.delete(*table.get_children())

    # set parameters
    table.column('Status', minwidth=47, width=69, anchor='center', stretch=True)
    table.column('Nickname', minwidth=80, width=102, anchor='center', stretch=True)
    table.column('Season', minwidth=47, width=69, anchor='center', stretch=True)
    table.column('Tank', minwidth=87, width=109, anchor='center', stretch=True)
    table.column('Damage', minwidth=87, width=109, anchor='center', stretch=True)
    table.column('Support', minwidth=87, width=109, anchor='center', stretch=True)
    table.column('Play time', minwidth=72, width=94, anchor='center', stretch=True)
    table.column('Win rate', minwidth=54, width=76, anchor='center', stretch=True)
    table.column('KD', minwidth=37, width=59, anchor='center', stretch=True)

    # push table and columns
    table.heading('Status', text='Status')
    table.heading('Nickname', text='Nickname')
    table.heading('Season', text='Season')
    table.heading('Tank', text='Tank')
    table.heading('Damage', text='Damage')
    table.heading('Support', text='Support')
    table.heading('Play time', text='Play time')
    table.heading('Win rate', text='Win rate')
    table.heading('KD', text='KD')
    table.pack(fill='both', expand=True)

    # set colors for certain tags
    table.tag_configure('Limited', background='#460000')
    table.tag_configure('Private', background='#460000')


def add_information_text_widget(text_widget, path):
    """If the file with Battle-tags exists > add these Battle-tags to the text-widget
       If the file with Battle-tags does not exist > it is ignored"""

    try:
        file_content = read_file(path=path)

        # add battle tags in text-widget
        battle_tags = file_content.get("Battle-tags", [])
        if battle_tags:
            formatted_tags = ",\n".join(battle_tags)  # convenient visual design
            text_widget.insert('1.0', formatted_tags)

        # set settings
        global max_workers
        max_workers = file_content['Settings']['max_workers']

    # file changed outside or not exist - rewrite the file
    except (json.decoder.JSONDecodeError, FileNotFoundError, AttributeError):
        overwriting_file(full_rewrite=True, path=path)


def save_button_click(text_widget, path):
    """Save battle-tags from text-widget"""

    # get data from text-widget
    data = text_widget.get('1.0', tk.END).strip()

    # split data by commas, remove extra spaces in each battle-tag
    new_battle_tags = [tag.strip() for tag in data.split(",")]

    # rewrite file with new datas
    overwriting_file(battle_tags_bool=True, battle_tags=new_battle_tags, path=path)


def battle_tags_button_click(save_button, table, text_frame, text_widget, path):
    """Open text-widget, change "Link" button to "Save" button"""

    # flag for stop check
    global user_want_stop
    user_want_stop = True

    # change button
    save_button.configure(text='Save', command=lambda: save_button_click(text_widget, path))

    # remove table-widget
    table.pack_forget()

    # open text-widget
    text_frame.pack(side="left", fill="both", expand=True)
    text_widget.pack(widget_info)


def check_button_click(check_button, save_button, text_frame, table, text_widget, path):
    """Performs a series of actions to retrieve information about each user entered in the text widget field"""

    # save information in text_widget then hide this
    global widget_info
    widget_info = text_widget.pack_info()
    text_widget.pack_forget()

    global user_want_stop
    user_want_stop = False  # to avoid problems in further clicks
    check_button.configure(state='disabled')  # block button

    try:
        # change button
        save_button.configure(text='Battle-tags', command=lambda: battle_tags_button_click(save_button=save_button, table=table, text_widget=text_widget, text_frame=text_frame, path=path))

        # push information on table
        battle_tags = read_file(path=path).get("Battle-tags")
        if len(battle_tags) > 0:
            if not user_want_stop:
                get_content(battle_tags=battle_tags, table=table, text_frame=text_frame)

    # when file with battle-tags not exist
    except FileNotFoundError:
        if not user_want_stop:
            ThreadPoolExecutor().submit(lambda: error_window(title='Error', text='List of battle-tags is empty!\nPlease click "save" button if you have not already'))

    check_button.configure(state='normal')  # unblock button
    user_want_stop = False


def get_content(battle_tags, table, text_frame):
    """1-st process of check_button_click
       Get content > record on right order > push to table"""

    global user_want_stop

    # error no battle tags
    if not battle_tags:
        ThreadPoolExecutor().submit(lambda: error_window(title='Error', text='List of battle tags is empty!'))

        # exit if needed
        if user_want_stop:
            return

    else:

        # clear content from lists
        private_profiles.clear()
        public_profiles.clear()
        limited_profiles.clear()
        error_occurred = False  # not to create more than one identical error window

        def request_processing(one_battle_tag):
            """2-nd process of check_button_click
               Add information in 3 lists"""
            information = process_get_content(battle_tag=one_battle_tag)

            # if needed exit
            if user_want_stop:
                return

            # record 3 different types to the relevant lists
            if information:
                if information[0] == 'Public':
                    public_profiles.append(information)
                elif information[0] == 'Limited':
                    limited_profiles.append(information)
                else:
                    private_profiles.append(information)

        # multithreaded request retrieval
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(request_processing, battle_tag) for battle_tag in battle_tags]

            # handle exceptions if any occur during the execution of threads
            for future, battle_tag in zip(futures, battle_tags):
                try:
                    future.result()

                # one error-window no more
                except requests.RequestException:
                    if not error_occurred:
                        error_occurred = True
                        ThreadPoolExecutor().submit(lambda: error_window(title='Error', text='Too many requests: Reduce the number of requests in the settings'))

        if user_want_stop:
            return

        # change widget on table
        text_frame.pack_forget()
        create_table_widget(table=table)

        # push content in the right order
        for unit in public_profiles:
            if user_want_stop:
                return
            table.insert('', tk.END, values=unit, tags=['Public'])
        for unit in limited_profiles:
            if user_want_stop:
                return
            table.insert('', tk.END, values=unit, tags=['Limited'])
        for unit in private_profiles:
            if user_want_stop:
                return
            table.insert('', tk.END, values=unit, tags=['Private'])


def process_get_content(battle_tag):
    """3-rd process of check_button_click
       Get content from API and return this data"""

    global user_want_stop

    # variables
    nickname = battle_tag.split("-")[0]
    tank_rating = '-'
    damage_rating = '-'
    support_rating = '-'
    time_played = '-'
    win_rate = '-'
    kd = '-'
    season = '-'

    if user_want_stop:
        return

    # get content from API
    response = requests.get(f'https://overfast-api.tekrop.fr/players/{battle_tag}').json()

    try:
        status = str(response['summary']['privacy']).capitalize()
        if status == 'Public':

            if type(response['summary']['competitive']) is dict:  # this return "None" if no competitive
                try:

                    # stats
                    season = response['summary']['competitive']['pc']['season']
                    stats = response['stats']['pc']['competitive']['career_stats']['all-heroes']
                    eliminations = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'eliminations')
                    deaths = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'deaths')
                    sec_played = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'time_played')
                    games_played = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_played')
                    games_won = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_won')

                    # stats calculation
                    time_played = f'{sec_played // 3600}hr {(sec_played % 3600) // 60}min'
                    win_rate = f"{(games_won / games_played) * 100:.2f}%"
                    kd = f'{eliminations / deaths:.2f}'

                    # tank rating
                    if type(response['summary']['competitive']['pc']['tank']) is dict:
                        tank_division = str(response['summary']['competitive']['pc']['tank']['division']).capitalize()
                        tank_division_tier = str(response['summary']['competitive']['pc']['tank']['tier'])
                        tank_rating = tank_division + '-' + tank_division_tier

                    if user_want_stop:
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

                # possibly could happen if no 'pc' stats
                except Exception as e:
                    if user_want_stop:
                        return
                    ThreadPoolExecutor().submit(lambda: error_window(title=f'{battle_tag}', text=f'Something went wrong: {e}'))

            else:  # no competitive
                status = 'Limited'
                return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

        # profile is closed
        else:
            return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

    # it happens when could not get blizzard page
    except KeyError:
        if user_want_stop is not True:
            ThreadPoolExecutor().submit(lambda: error_window(title='Error', text=f'{battle_tag}: Timeout exceeded.'))
        return


def open_settings_window(window, path):
    """Setting window"""
    global max_workers

    # set window-setting
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.resizable(False, False)  # prevent window resizing
    settings_window.attributes('-topmost', True)  # window on top
    settings_window.grab_set()  # make the settings window modal

    # set size
    settings_window_width = 300
    settings_window_height = 150
    setting_screen_width = settings_window.winfo_screenwidth()
    setting_screen_height = settings_window.winfo_screenheight()
    setting_x_cord = int((setting_screen_width / 2) - (settings_window_width / 2))
    setting_y_cord = int((setting_screen_height / 2) - (settings_window_height / 2))
    settings_window.geometry(f"{settings_window_width}x{settings_window_height}+{setting_x_cord}+{setting_y_cord}")

    settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)

    # empty cell for top indent
    empty_label_top = tk.Label(settings_window)
    empty_label_top.grid(row=0, column=0)

    # text "Number of requests" and field for entering number
    label = tk.Label(settings_window, text="Number of requests")
    label.grid(row=1, column=0, padx=5)
    num_requests_var = tk.StringVar(value=str(max_workers))
    entry = tk.Spinbox(settings_window, from_=1, to=6, textvariable=num_requests_var, width=5)
    entry.grid(row=1, column=1, padx=5)

    # button save
    save_button_width = 8
    x_button = settings_window_width // 2
    y_button = settings_window_height - 30  # indent down
    setting_save_button = ttk.Button(settings_window, text="Save", width=save_button_width, command=lambda: settings_save_click())
    setting_save_button.place(x=x_button, y=y_button, anchor='center')

    # top right buttons style
    settings_window.wm_attributes("-toolwindow", 1) if tk.TkVersion >= 8.5 and sys.platform.startswith('win') else None

    def settings_save_click():
        """Save max_workers value and destroy window"""
        global max_workers
        max_workers = int(num_requests_var.get())
        overwriting_file(max_workers_bool=True, path=path)
        settings_window.destroy()


def error_window(title: str, text: str):
    """Call error window"""
    return messagebox.showerror(title, text)


def exit_main_window(text_widget, path):
    """If you forgot to save the file, you are prompted to do so"""

    # get battle tags from file
    battle_tags_file = read_file(path=path).get("Battle-tags", [])

    # get battle-tags from text-widget
    data = text_widget.get('1.0', tk.END).strip()
    battle_tags_widget = [tag.strip() for tag in data.split(",")]  # split data by commas, remove extra spaces in each battle-tag

    # question: save text or not if text-widget content and file content different
    if set(battle_tags_file) != set(battle_tags_widget):
        if messagebox.askquestion(title='Exit', message='Are you want to save your battle-tags list?') == 'yes':
            save_button_click(text_widget=text_widget, path=path)

    # close
    os.kill(os.getpid(), signal.SIGTERM)
