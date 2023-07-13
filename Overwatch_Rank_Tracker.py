import tkinter as tk
from tkinter import ttk, messagebox
import requests
from concurrent.futures import ThreadPoolExecutor

import functions

# TODO:
#  1. Fix error - when double click on check > two processes
#  2. Question window before exit app > save information in text-widget or not
#  3. Move all functions in functions.py
#  4. Multitasking

# create main window
window = tk.Tk()
window.title('Overwatch Rank Tracker')
window.geometry('800x600')
window.configure(bg='#2B2B2B')
window.minsize(800, 600)

# set style for window
style = ttk.Style(window)
style.theme_use("clam")
style.configure('Treeview', background='#2B2B2B', foreground="white", fieldbackground="#2B2B2B")

# create global variables
public_profiles = []
limited_profiles = []
private_profiles = []
table = ttk.Treeview(window, columns=['Status', 'Nickname', 'Season', 'Tank', 'Damage', 'Support', 'Play time', 'Win rate', 'KD'], show='headings', height=26)

# set size and centering
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_cord = int((screen_width / 2) - (800 / 2))
y_cord = int((screen_height / 2) - (600 / 2))
window.geometry("{}x{}+{}+{}".format(800, 600, x_cord, y_cord))


def check_button_click():
    """Performs a series of actions to retrieve information about each user entered in the text widget field"""

    check_button.configure(state='disabled')  # block button
    try:
        with open('saved_battle_tags.json', 'r') as file:

            # change button
            save_button.configure(text='Links', command=links_button_click)

            # change widget on table
            text_frame.pack_forget()
            create_table_widget()

            # push information on table
            battle_tags = file.read().strip()
            if battle_tags:
                battle_tags = battle_tags.split(',')
                battle_tags = [unit.strip() for unit in battle_tags if unit.strip() != '']
                get_content(battle_tags)
            check_button.configure(state='normal')  # unblock button

    # when file with battle-tags not exist
    except FileNotFoundError:
        check_button.configure(state='normal')  # unblock button
        messagebox.showerror('Error', 'List of battle-tags is empty!\nPlease click "save" button if you have not already')


def save_button_click():
    """Saves information from text-widget"""

    # get information from text-widget
    data = text_widget.get('1.0', tk.END)

    # save the information
    with open('saved_battle_tags.json', 'w') as f:
        f.write(data)


def links_button_click():
    """Open text-widget, change "Link" button to "Save" button"""

    # change button
    save_button.configure(text='Save', command=save_button_click)

    # remove table-widget
    table.pack_forget()

    # open text-widget
    text_frame.pack(side="left", fill="both", expand=True)


def create_table_widget():
    """Create table-widget, columns = 9
       for 800x600, full length = 796
       if you set the minimum length for all columns, full length = 598"""

    # delete information from the table if it exists
    if table.get_children():
        table.delete(*table.get_children())

    # set parameters
    table.column('Status', minwidth=47, width=69, anchor='center', stretch=False)
    table.column('Nickname', minwidth=80, width=102, anchor='center', stretch=False)
    table.column('Season', minwidth=47, width=69, anchor='center', stretch=False)
    table.column('Tank', minwidth=87, width=109, anchor='center', stretch=False)
    table.column('Damage', minwidth=87, width=109, anchor='center', stretch=False)
    table.column('Support', minwidth=87, width=109, anchor='center', stretch=False)
    table.column('Play time', minwidth=72, width=94, anchor='center', stretch=False)
    table.column('Win rate', minwidth=54, width=76, anchor='center', stretch=False)
    table.column('KD', minwidth=37, width=59, anchor='center', stretch=False)

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


def get_content(battle_tags):
    """Get content > record on right order > push to table"""
    if not battle_tags:
        messagebox.showerror('Error', 'List of battle tags is empty!')
    else:

        # clear content from lists
        private_profiles.clear()
        public_profiles.clear()
        limited_profiles.clear()

        # add content in lists
        for i in battle_tags:
            information = process_get_content(i)

            # record 3 different types to the relevant lists
            if information:
                if information[0] == 'Public':
                    public_profiles.append(information)
                elif information[0] == 'Limited':
                    limited_profiles.append(information)
                else:
                    private_profiles.append(information)

        # push content in the right order
        for unit in public_profiles:
            table.insert('', tk.END, values=unit, tags=['Public'])
        for unit in limited_profiles:
            table.insert('', tk.END, values=unit, tags=['Limited'])
        for unit in private_profiles:
            table.insert('', tk.END, values=unit, tags=['Private'])


def process_get_content(unit):
    """Get content from API and return this data"""

    # values
    nickname = unit.split("-")[0]
    tank_rating = '-'
    damage_rating = '-'
    support_rating = '-'
    time_played = '-'
    win_rate = '-'
    kd = '-'
    season = '-'

    # get content from API
    response = requests.get(f'https://overfast-api.tekrop.fr/players/{unit}').json()

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
                    messagebox.showerror(f'{unit}', f'Something went wrong: {e}')

            else:  # no competitive
                status = 'Limited'
                return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

        # profile is closed
        else:
            return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

    # it happens when could not get blizzard page
    except KeyError:
        messagebox.showerror('Error', f'{unit}: {response["error"]}.')
        return


# set button_frame
button_frame = tk.Frame(window, bg='#2B2B2B')
button_frame.pack(side='bottom', fill='x')

# set text_frame for text_widget
text_frame = tk.Frame(window, bg="#2B2B2B")
text_frame.pack(side="left", fill="both", expand=True)

# set buttons
check_button = tk.Button(button_frame, text='Check', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: ThreadPoolExecutor().submit(check_button_click))
save_button = tk.Button(button_frame, text='Save', font=('Calibri', 17, 'bold'), pady=3, width=16, command=save_button_click)
exit_button = tk.Button(button_frame, text='Exit', font=('Calibri', 17, 'bold'), pady=3, width=16, command=window.destroy)
check_button.pack(side='left', fill='x', expand=True)
save_button.pack(side='left', fill='x', expand=True)
exit_button.pack(side='left', fill='x', expand=True)

# create text-widget
text_widget = tk.Text(text_frame, font=('Calibri', 13, 'bold'), fg='#A0A0A0', insertbackground='white', padx=10, pady=15, bg="#2B2B2B", relief='flat')
text_widget.pack(side='left', fill='both', expand=True)
functions.add_information_text_widget(text_widget)
functions.create_scrollbar(text_frame, text_widget)

# launch
window.mainloop()
