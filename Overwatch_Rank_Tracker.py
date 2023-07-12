import concurrent
import tkinter as tk
from tkinter import ttk
import requests
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox

# TODO:
#  1. Function "create_scrollbar" must work for table.
#  2. Edit error window.

window = tk.Tk()
window.title('Overwatch Rank Tracker')
window.geometry('800x600')
window.configure(bg='#2B2B2B')
window.minsize(800, 600)
button_frame = tk.Frame(window, bg='#2B2B2B')
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_cord = int((screen_width / 2) - (800 / 2))
y_cord = int((screen_height / 2) - (600 / 2))
window.geometry("{}x{}+{}+{}".format(800, 600, x_cord, y_cord))
public = []
limited = []
private = []


def create_text_widget():
    """
    Text widget for battle tags.
    Appears when user clicks on links or when the program starts
    """
    global text_frame, text_widget
    text_frame = tk.Frame(window, bg="#2B2B2B")
    text_frame.pack(side="left", fill="both", expand=True)
    text_widget = tk.Text(text_frame, font=('Calibri', 13, 'bold'), fg='#A0A0A0', insertbackground='white', padx=10, pady=15, bg="#2B2B2B", relief='flat')
    text_widget.pack(side='left', fill='both', expand=True)
    try:
        with open('saved_text.json', 'r') as f:
            data = f.read().strip()
            if data:
                text_widget.insert('1.0', data)
    except FileNotFoundError:
        pass


def create_scrollbar():
    """ Creates scroll bar for text_widget """
    scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
    scrollbar.pack(side='right', fill='y', pady=10)
    text_widget.config(yscrollcommand=scrollbar.set)


def check():
    """ Button check. Change button "Save" to "Links." Starts process-check """
    save_button.configure(text='Links', command=links)
    executor = ThreadPoolExecutor()
    executor.submit(process_check)


def process_check():
    """ Get information from API, sort these datas to table, forget text_widget"""
    save_button.configure(text='Links', command=links)
    text_frame.pack_forget()
    create_table()
    try:
        with open('saved_text.json', 'r') as f:
            battle_tags = f.read().strip()
            if battle_tags:
                battle_tags = battle_tags.split(',')
                battle_tags = [unit.strip() for unit in battle_tags if unit.strip() != '']
                get_content(battle_tags)
    except FileNotFoundError:
        pass


def save():
    """ Save change in text_widget """
    data = text_widget.get('1.0', tk.END)
    if data.strip() != '':
        with open('saved_text.json', 'w') as f:
            f.write(data)


def links():
    """ Change button "links" to "Save" """
    save_button.configure(text='Save', command=save)
    table.pack_forget()
    text_frame.pack(side="left", fill="both", expand=True)


def create_table():
    """ Create table """
    global table
    if 'table' in globals():
        table.destroy()
    table = ttk.Treeview(window, columns=['Status', 'Nickname', 'Season', 'Tank', 'Damage', 'Support', 'Play time', 'Win rate', 'KD'], show='headings', height=26)
    # 796 max length
    # with min its 598
    table.column('Status', minwidth=69, width=69, anchor='center', stretch=False)  # min - 47
    table.column('Nickname', minwidth=102, width=102, anchor='center', stretch=False)  # min - 80
    table.column('Season', minwidth=69, width=69, anchor='center', stretch=False)  # min - 47
    table.column('Tank', minwidth=109, width=109, anchor='center', stretch=False)  # min - 87
    table.column('Damage', minwidth=109, width=109, anchor='center', stretch=False)  # min - 87
    table.column('Support', minwidth=109, width=109, anchor='center', stretch=False)  # min - 87
    table.column('Play time', minwidth=94, width=94, anchor='center', stretch=False)  # min - 72
    table.column('Win rate', minwidth=76, width=76, anchor='center', stretch=False)  # min - 54
    table.column('KD', minwidth=59, width=59, anchor='center', stretch=False)  # min - 37
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
    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure('Treeview', background='#2B2B2B', foreground="white", fieldbackground="#2B2B2B")
    table.tag_configure('Limited', background='#460000')
    table.tag_configure('Private', background='#460000')


def something(battle_tags):
    information = process_get_content(battle_tags)
    if information:
        if information[0] == 'Public':
            public.append(information)
        elif information[0] == 'Limited':
            limited.append(information)
        else:
            private.append(information)


def get_content(battle_tags):
    if not battle_tags:
        messagebox.showerror('Error', 'The list of battle tags is empty')
    else:
        private.clear()
        public.clear()
        limited.clear()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(something, battle_tags)
        print(f'public = {len(public)}, expected = 6')
        print(f'limited = {len(limited)}, expected = 1')
        print(f'private = {len(private)}, expected = 11')
        print(f'count = {len(public)+len(limited)+len(private)}, expected = 18')
        for unit in public:
            table.insert('', tk.END, values=unit, tags=['Public'])
        for unit in limited:
            table.insert('', tk.END, values=unit, tags=['Limited'])
        for unit in private:
            table.insert('', tk.END, values=unit, tags=['Private'])


def process_get_content(unit):
    nickname = unit.split("-")[0]
    tank_rating = '-'
    damage_rating = '-'
    support_rating = '-'
    time_played = '-'
    win_rate = '-'
    kd = '-'
    season = '-'
    response = requests.get(f'https://overfast-api.tekrop.fr/players/{unit}').json()

    try:
        status = str(response['summary']['privacy']).capitalize()

        if status == 'Public':

            if type(response['summary']['competitive']) is dict:

                try:  # competitive

                    season = response['summary']['competitive']['pc']['season']

                    # stats
                    stats = response['stats']['pc']['competitive']['career_stats']['all-heroes']
                    eliminations = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'eliminations')
                    deaths = next(stat['value'] for hero in stats for stat in hero['stats'] if stat['key'] == 'deaths')

                    sec_played = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'time_played')
                    games_played = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_played')
                    games_won = next(stat['value'] for hero in stats if hero['category'] == 'game' for stat in hero['stats'] if stat['key'] == 'games_won')

                    time_played = f'{sec_played // 3600}hr {(sec_played % 3600) // 60}min'
                    win_rate = f"{(games_won / games_played) * 100:.2f}%"
                    kd = f'{eliminations / deaths:.2f}'

                    # rating
                    if type(response['summary']['competitive']['pc']['tank']) is dict:
                        tank_division = str(response['summary']['competitive']['pc']['tank']['division']).capitalize()
                        tank_division_tier = str(response['summary']['competitive']['pc']['tank']['tier'])
                        tank_rating = tank_division + '-' + tank_division_tier

                    if type(response['summary']['competitive']['pc']['damage']) is dict:
                        damage_division = str(response['summary']['competitive']['pc']['damage']['division']).capitalize()
                        damage_division_tier = str(response['summary']['competitive']['pc']['damage']['tier'])
                        damage_rating = damage_division + '-' + damage_division_tier

                    if type(response['summary']['competitive']['pc']['support']) is dict:
                        support_division = str(response['summary']['competitive']['pc']['support']['division']).capitalize()
                        support_division_tier = str(response['summary']['competitive']['pc']['support']['tier'])
                        support_rating = support_division + '-' + support_division_tier
                    return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

                except Exception as e:  # Possibly could happen if no 'pc' stats
                    messagebox.showerror(f'{unit}', f'Something went wrong: {e}')
            else:  # no competitive
                status = 'Limited'
                return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

        else:  # Profile is closed
            return status, nickname, season, tank_rating, damage_rating, support_rating, time_played, win_rate, kd

    except KeyError:  # It happens when couldn't get blizzard page
        messagebox.showerror('Error', f'{unit}: {response["error"]}.')
        return


check_button = tk.Button(button_frame, text='Check', font=('Calibri', 17, 'bold'), pady=3, width=16, command=check)
save_button = tk.Button(button_frame, text='Save', font=('Calibri', 17, 'bold'), pady=3, width=16, command=save)
exit_button = tk.Button(button_frame, text='Exit', font=('Calibri', 17, 'bold'), pady=3, width=16, command=window.destroy)
check_button.pack(side='left', fill='x', expand=True)
save_button.pack(side='left', fill='x', expand=True)
exit_button.pack(side='left', fill='x', expand=True)
button_frame.pack(side='bottom', fill='x')
create_text_widget()
create_scrollbar()
window.mainloop()
