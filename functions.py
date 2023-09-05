import concurrent
import io
import os
import re
import signal
import subprocess
from tkinter import ttk, messagebox, Text, Tk, Button, Toplevel
import tkinter as tk
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import sys
import logging


# set logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s], %(levelname)s: %(message)s in %(name)s.py', datefmt='%Y-%m-%d, %H:%M:%S')
logger = logging.getLogger(__name__)

# create global variables
public_profiles = []
limited_profiles = []
private_profiles = []
user_want_stop = False
error_battle_tags = []
text_widget_content = ""

# initial settings
max_workers = 6


def check_for_updates(owner_name: str, repo_name: str, current_version: str, token: str):
    """Checks the current version against the current version and starts an external update process if necessary."""

    response = None

    try:

        # request for the latest release version
        response = requests.get(f"https://api.github.com/repos/{owner_name}/{repo_name}/releases/latest")

        # error handling
        if response.status_code != 200:
            ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', text=f'While getting latest version, error code {response.status_code}.'))
            return

        # get information
        latest_release = response.json()

        # get the name of the latest version
        latest_version = latest_release['name']

        # versions are different - request for update
        if latest_version != current_version:

            # ask the user if he wants to upgrade
            question = messagebox.askyesno(title="Update is available", message="Do you want to update?")

            # user wants updates
            if question:

                # run auto-update
                subprocess.Popen(['Updater.exe'], shell=True)

                # finishing the main process
                sys.exit()

    # no internet connection - no update
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Update Error", "Internet connection problem.")

    # unexpected error
    except Exception as error:
        title, text = get_logs(error=error)
        sending_logs(owner_name=owner_name, token=token, title=title, text=text, api_response=response.json(), status_code=response.status_code)
        messagebox.showerror("Update Error", f"Unexpected error occurred while checking for updates. \n{error}")


def get_logs(error: Exception):
    """Creates a log entry for an error and returns its title and full text."""

    log_buffer = io.StringIO()
    handler = logging.StreamHandler(log_buffer)
    handler.setFormatter(logging.Formatter('[%(asctime)s], %(levelname)s: %(message)s in %(name)s.py', datefmt='%Y-%m-%d, %H:%M:%S'))
    logger.addHandler(handler)
    logger.error(f'{error}', exc_info=True)
    log_text = log_buffer.getvalue()
    log_title = log_text.split('\n')[0]

    return log_title, log_text


def sending_logs(api_response: dict, owner_name: str, token: str, title: str, text: str, status_code: int):
    """Sending logs, this is used only for an unexpected error."""

    try:

        # content
        data = {
            "Date": re.search(r'\[(.*?)]', text).group(1),
            "File": re.search(r'\w+\.py', text).group(0),
            "Error": re.search(r': (.*?)(?= in)', text).group(1),
            "Traceback": {
                'content': text.splitlines()[1:],
                'type': 'text/plain'
            },
            "Response status code": status_code,
            "Response content": {
                'content': api_response,
                'type': 'application/json'
            }
        }

        # send logs
        requests.post("https://api.github.com/gists", auth=(owner_name, token),
                      json={
                          "description": title,
                          "public": False,
                          "files": {
                              "content.json": {
                                  "content": json.dumps(data, indent=4)
                              }
                          }
        })

    # error handling
    except requests.exceptions.HTTPError:
        pass


def create_loading_text(ort):
    """Adds the text "Loading..." to the widget_frame."""

    label = tk.Label(ort.widget_frame, text='Loading...', font=('Calibri', 13, 'bold'), fg='#A0A0A0', bg="#2B2B2B")
    label.place(relx=0.5, rely=0.5, anchor='center')


def create_table_widget(ort):
    """Create table-widget. Columns = 9, full length for 800x600 = 796."""

    # set table
    table_widget = ttk.Treeview(ort.widget_frame, columns=['Status', 'Nickname', 'Season', 'Tank', 'Damage', 'Support', 'Play time', 'Win rate', 'KD'], show='headings', height=26)

    # set parameters
    table_widget.column('Status', minwidth=47, width=66, anchor='center', stretch=True)
    table_widget.column('Nickname', minwidth=134, width=156, anchor='center', stretch=True)
    table_widget.column('Season', minwidth=35, width=57, anchor='center', stretch=True)
    table_widget.column('Tank', minwidth=87, width=100, anchor='center', stretch=True)
    table_widget.column('Damage', minwidth=87, width=100, anchor='center', stretch=True)
    table_widget.column('Support', minwidth=87, width=100, anchor='center', stretch=True)
    table_widget.column('Play time', minwidth=72, width=91, anchor='center', stretch=True)
    table_widget.column('Win rate', minwidth=54, width=73, anchor='center', stretch=True)
    table_widget.column('KD', minwidth=37, width=56, anchor='center', stretch=True)

    # push table and columns
    table_widget.heading('Status', text='Status')
    table_widget.heading('Nickname', text='Nickname')
    table_widget.heading('Season', text='Season')
    table_widget.heading('Tank', text='Tank')
    table_widget.heading('Damage', text='Damage')
    table_widget.heading('Support', text='Support')
    table_widget.heading('Play time', text='Play time')
    table_widget.heading('Win rate', text='Win rate')
    table_widget.heading('KD', text='KD')
    table_widget.pack(fill='both', expand=True)

    # set colors for certain tags
    table_widget.tag_configure(tagname='Limited', background='#460000')
    table_widget.tag_configure(tagname='Private', background='#460000')

    # set widget for further closure
    ort.widget = table_widget


def create_text_widget(ort):
    """Create a text widget and add information to it from a local file or previously used ready text."""

    # create text widget
    text_widget = tk.Text(ort.widget_frame, font=('Calibri', 13, 'bold'), fg='#A0A0A0', insertbackground='white', padx=10, pady=15, bg="#2B2B2B", relief='flat')
    text_widget.pack(side='left', fill='both', expand=True)

    # user has not entered information before
    global text_widget_content
    if not text_widget_content:
        try:

            # read battle-tags from file
            file_content = read_file(path=ort.path_to_file)
            battle_tags = file_content.get("Battle-tags", [])
            if battle_tags:

                # convenient visual design
                text_widget_content = ",\n".join(battle_tags)

        # file changed outside or not exist - rewrite the file
        except (json.decoder.JSONDecodeError, FileNotFoundError, AttributeError):
            overwriting_file(full_rewrite=True, path=ort.path_to_file)

    # insert information into a text widget
    text_widget.insert('1.0', text_widget_content)

    # create scroll-bar
    text_widget.scrollbar = ttk.Scrollbar(ort.widget_frame, command=text_widget.yview)
    text_widget.scrollbar.pack(side='right', fill='y', pady=10)
    text_widget.config(yscrollcommand=text_widget.scrollbar.set)

    # set widget for further closure
    ort.widget = text_widget


def destroy_widget(ort):
    """Removing a widget from the main window."""

    # user may have already entered some information
    global text_widget_content

    # for text-widget
    if type(ort.widget) is Text:

        # remove the scroll-bar from widget_frame
        ort.widget.scrollbar.destroy()

        # record text-widget content
        text_widget_content = ort.widget.get("1.0", tk.END).strip()

    # destroy widget
    ort.widget.destroy()
    ort.widget = None


def exit_main_window(ort):
    """If you forgot to save the file, you are prompted to do so."""

    global text_widget_content

    # get battle-tags from file
    battle_tags_file = read_file(path=ort.path_to_file).get("Battle-tags", [])

    # current widget - text widget, get current content
    if type(ort.widget) is Text:
        text_widget_content = ort.widget.get("1.0", tk.END).strip()

    # content adjustment, split data by commas, remove extra spaces in each battle-tag
    text_widget_content = [tag.strip() for tag in text_widget_content.split(",")]

    # question: save text or not if text-widget content and file content different
    if set(battle_tags_file) != set(text_widget_content):
        if messagebox.askquestion(title='Exit', message='Are you want to save your battle-tags list?') == 'yes':
            save_button_click(widget=ort.widget, path_to_file=ort.path_to_file)

    # close
    os.kill(os.getpid(), signal.SIGTERM)


def window_centering(window: Tk or Toplevel, window_width: int, window_height: int):
    """Centering the window so that it starts in the middle."""

    # display sizing
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate the x and y coordinates to center the window on the screen
    x_cord = int((screen_width / 2) - (window_width / 2))
    y_cord = int((screen_height / 2) - (window_height / 2))

    # set the window's geometry to center it on the screen
    window.geometry(f"{window_width}x{window_height}+{x_cord}+{y_cord}")


def open_settings_window(ort, window: Tk):
    """Setting window."""

    global max_workers

    # set window-setting
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.resizable(False, False)  # prevent window resizing
    settings_window.attributes('-topmost', True)  # window on top
    settings_window.grab_set()  # make the settings window modal (blocks access to other windows while the window is open)
    settings_window.protocol("WM_DELETE_WINDOW", settings_window.destroy)  # custom close
    settings_window_height = 120
    settings_window_width = 190
    window_centering(window=settings_window, window_width=settings_window_width, window_height=settings_window_height)

    # empty cell for top indent
    empty_label_top = tk.Label(settings_window)
    empty_label_top.grid(row=0, column=0)

    # "Number of requests" text
    label = tk.Label(settings_window, text="Number of requests")
    label.grid(row=1, column=0, padx=5)

    # "Number of requests" field for entering number
    num_requests_var = tk.StringVar(value=str(max_workers))
    entry = tk.Spinbox(settings_window, from_=1, to=6, textvariable=num_requests_var, width=5)
    entry.grid(row=1, column=1, padx=5)

    # button save
    x_button = settings_window_width // 2
    y_button = settings_window_height - 30
    setting_save_button = ttk.Button(settings_window, text="Save", width=8, command=lambda: settings_save_click())
    setting_save_button.place(x=x_button, y=y_button, anchor='center')

    # top right buttons style
    settings_window.wm_attributes("-toolwindow", 1) if tk.TkVersion >= 8.5 and sys.platform.startswith('win') else None

    def settings_save_click():
        """Save max_workers value and destroy window."""

        # change max_workers value
        global max_workers
        max_workers = int(num_requests_var.get())

        overwriting_file(max_workers_bool=True, path=ort.path_to_file)
        settings_window.destroy()


def set_settings(path_to_file: str):
    """Set settings for further use in the code."""

    try:

        # read file
        file_content = read_file(path=path_to_file)

        # set settings
        global max_workers
        max_workers = file_content['Settings']['max_workers']

    # file changed outside or not exist - rewrite the file
    except (json.decoder.JSONDecodeError, FileNotFoundError, AttributeError):
        overwriting_file(full_rewrite=True, path=path_to_file)


def read_file(path: str):
    """Returns the contents of a file."""

    with open(path, 'r') as file:
        return json.load(file)


def write_file(path: str, paste: dict):
    """Record file with new content."""

    with open(path, 'w') as file:
        json.dump(paste, file, indent=2)


def overwriting_file(path: str, max_workers_bool: bool = False, battle_tags_bool: bool = False, battle_tags: list = None, full_rewrite: bool = False):
    """Overwrite file or certain blocks in file."""

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


def save_button_click(widget: Text, path_to_file: str):
    """Save battle-tags from text-widget."""

    # get data from text-widget
    data = widget.get('1.0', tk.END).strip()

    # split data by commas, remove extra spaces in each battle-tag
    new_battle_tags = [tag.strip() for tag in data.split(",")]

    # rewrite file with new datas
    overwriting_file(battle_tags_bool=True, battle_tags=new_battle_tags, path=path_to_file)


def battle_tags_button_click(ort, save_button: Button):
    """Open text-widget, change "Link" button to "Save" button."""

    # flag for stop check
    global user_want_stop
    user_want_stop = True

    # change button
    save_button.configure(text='Save', command=lambda: save_button_click(widget=ort.widget, path_to_file=ort.path_to_file))

    # remove table-widget
    destroy_widget(ort=ort)

    # create text-widget
    create_text_widget(ort=ort)


def check_button_click(ort, check_button: Button, save_button: Button):
    """Performs a series of actions to retrieve information about each user entered in the text widget field."""

    # to avoid problems in further clicks
    global user_want_stop
    user_want_stop = False

    # block button
    check_button.configure(state='disabled')

    try:

        # change button
        save_button.configure(text='Battle-tags', command=lambda: battle_tags_button_click(ort=ort, save_button=save_button))

        # get information from text widget
        battle_tags = ort.widget.get('1.0', tk.END).strip()

        # information available
        if battle_tags:

            # battle-tags list
            battle_tags = [tag.strip() for tag in battle_tags.split(",")]

            # delete text-widget
            if not user_want_stop:
                destroy_widget(ort=ort)

                # push information on table
                try:
                    get_content_and_push(ort=ort, battle_tags=battle_tags)

                # no internet connection - to bring it all back and give an error
                except requests.exceptions.ConnectionError:

                    # revert the text widget back
                    destroy_widget(ort=ort)
                    create_text_widget(ort=ort)

                    # change button back
                    save_button.configure(text='Save', command=lambda: save_button_click(widget=ort.widget, path_to_file=ort.path_to_file))

                    # message error
                    messagebox.showerror("Connection Error", "Internet connection problem.")

        # no battle-tags - raise error
        else:
            raise ValueError

    # error window - no battle tags
    except ValueError:
        ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', text='List of battle tags is empty.'))

    # unblock button
    check_button.configure(state='normal')

    # reset flag
    user_want_stop = False


def get_content_and_push(ort, battle_tags: list):
    """Getting the information for each of the battle-tags and adding this to table-widget in the correct order."""

    # clear content from lists
    private_profiles.clear()
    public_profiles.clear()
    limited_profiles.clear()

    # not to create more than one identical error window
    error_occurred = False

    # multithreaded request retrieval
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_and_sort_account, ort, battle_tag) for battle_tag in battle_tags]

        global user_want_stop
        if user_want_stop:
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
                    ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', text='Too many requests: Reduce the number of requests in the settings.\n'
                                                                                                 'If it does not help, there may be a problem:\n\n'
                                                                                                 '1. Problem in the server.\n'
                                                                                                 '2. Check if you added the battle tags correctly.\n'))

    if user_want_stop:
        return

    create_table_widget(ort=ort)

    # error window if battle-tag(s) was not found
    if len(error_battle_tags) > 0:
        ThreadPoolExecutor().submit(lambda: messagebox.showerror(title='Error', text=f'This accounts ({", ".join(map(str, error_battle_tags))}) was not found.'))

    # push content in the right order
    for unit in public_profiles:
        if user_want_stop:
            return
        ort.widget.insert('', tk.END, values=unit, tags=['Public'])
    for unit in limited_profiles:
        if user_want_stop:
            return
        ort.widget.insert('', tk.END, values=unit, tags=['Limited'])
    for unit in private_profiles:
        if user_want_stop:
            return
        ort.widget.insert('', tk.END, values=unit, tags=['Private'])


def process_and_sort_account(ort, one_battle_tag: str):
    """Sort an account by status into a separate list."""

    information = get_and_process_single_account_info(battle_tag=one_battle_tag, owner_name=ort.owner_name, token=ort.token)

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


def get_and_process_single_account_info(battle_tag: str, owner_name: str, token: str):
    """Getting information from API on one account and then processing it."""

    # variables
    nickname = battle_tag.split("-")[0] + '#' + battle_tag.split("-")[1]
    tank_rating = '-'
    damage_rating = '-'
    support_rating = '-'
    time_played = '-'
    win_rate = '-'
    kd = '-'
    season = '-'

    global user_want_stop
    if user_want_stop:
        return

    # get content from API
    response = requests.get(f'https://overfast-api.tekrop.fr/players/{battle_tag}')
    status_code = response.status_code
    response = response.json()

    # record and return data
    try:
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

                # unexpected error
                except Exception as error:
                    if user_want_stop:
                        return

                    # send logs
                    title, text = get_logs(error=error)
                    sending_logs(owner_name=owner_name, token=token, title=title, text=text, api_response=response, status_code=status_code)

                    # error window
                    ThreadPoolExecutor().submit(lambda e=error: messagebox.showerror(title=f'{battle_tag}', text=f'Sorry, something went wrong. {e}'))

            # no competitive
            else:
                status = 'Limited'
                return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

        # profile is closed
        else:
            return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

    # it happens when could not get blizzard page
    except KeyError:
        if user_want_stop is not True:

            # add a battle-tag to further output a single error with multiple or single battle-tags
            error_battle_tags.append(battle_tag)

        return
