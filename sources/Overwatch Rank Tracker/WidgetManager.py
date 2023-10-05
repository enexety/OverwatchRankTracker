import json
import tkinter
from tkinter import ttk, Text


class WidgetManager:

    def __init__(self):
        self.widget_frame = None
        self.current_widget = None
        self.text_widget_content = None
        self.scrollbar = None

    def set_widget_frame(self, main_window):
        """Creates a frame for the widget."""

        self.widget_frame = tkinter.Frame(main_window, bg="#2B2B2B")
        self.widget_frame.pack(side="top", fill="both", expand=True)

    def destroy_widget(self):
        """Removing a widget from the main window."""

        # for text-widget
        if type(self.current_widget) is Text:
            # remove the scroll-bar from widget_frame
            self.scrollbar.pack_forget()

            # record text-widget content
            self.text_widget_content = self.current_widget.get("1.0", tkinter.END).strip()

        # destroy widget
        if self.current_widget is not None:
            self.current_widget.destroy()
            self.current_widget = None

    def create_scrollbar(self, widget, frame):
        """Creating a scrollbar or reverting it back."""

        # create a scrollbar if not previously created
        if not self.scrollbar:
            self.scrollbar = ttk.Scrollbar(frame, command=widget.yview)

        # insert into the widget and bind it to it
        self.scrollbar.pack(side='right', fill='y', pady=10)
        widget.config(yscrollcommand=self.scrollbar.set)

    def create_text_widget(self, fileManager):
        """Create a text-widget and add information to it from a local file or previously used ready text."""

        # create text widget
        self.current_widget = tkinter.Text(self.widget_frame, font=('Calibri', 13, 'bold'), fg='#A0A0A0', insertbackground='white', padx=10, pady=15, bg="#2B2B2B", relief='flat')
        self.current_widget.pack(side='left', fill='both', expand=True)

        # create scroll-bar
        self.create_scrollbar(widget=self.current_widget, frame=self.widget_frame)

        # user has not entered information before
        if not self.text_widget_content:
            try:

                # read battle-tags from file
                file_content = fileManager.read_file()
                battle_tags = file_content.get("Battle-tags", [])
                if battle_tags:
                    # convenient visual design
                    self.text_widget_content = ",\n".join(battle_tags)

            # file changed outside or not exist - rewrite the file
            except (json.decoder.JSONDecodeError, FileNotFoundError, AttributeError):
                fileManager.overwriting_file(full_rewrite=True)

        # insert information into a text widget
        if self.text_widget_content is not None:
            self.current_widget.insert('1.0', self.text_widget_content)

    def create_table_widget(self):
        """Create table-widget. Columns = 9, full length for 800x600 = 796."""

        # destroy widget
        self.destroy_widget()

        # set table
        self.current_widget = ttk.Treeview(self.widget_frame, columns=['Status', 'Nickname', 'Season', 'Tank', 'Damage', 'Support', 'Play time', 'Win rate', 'KD'], show='headings', height=26)

        # set parameters
        self.current_widget.column(column='Status', minwidth=47, width=63, anchor='center', stretch=False)
        self.current_widget.column(column='Nickname', minwidth=134, width=156, anchor='center', stretch=True)
        self.current_widget.column(column='Season', minwidth=35, width=57, anchor='center', stretch=False)
        self.current_widget.column(column='Tank', minwidth=87, width=100, anchor='center', stretch=True)
        self.current_widget.column(column='Damage', minwidth=87, width=100, anchor='center', stretch=True)
        self.current_widget.column(column='Support', minwidth=87, width=100, anchor='center', stretch=True)
        self.current_widget.column(column='Play time', minwidth=72, width=91, anchor='center', stretch=True)
        self.current_widget.column(column='Win rate', minwidth=54, width=73, anchor='center', stretch=True)
        self.current_widget.column(column='KD', minwidth=37, width=56, anchor='center', stretch=True)

        # push table and columns
        self.current_widget.heading(column='Status', text='Status', command=lambda: self.sort_table(column_name='Status', reverse=True, column_index=0))
        self.current_widget.heading(column='Nickname', text='Nickname', command=lambda: self.sort_table(column_name='Nickname', reverse=False, column_index=1))
        self.current_widget.heading(column='Season', text='Season', command=lambda: self.sort_table(column_name='Season', reverse=True, column_index=2))
        self.current_widget.heading(column='Tank', text='Tank', command=lambda: self.sort_table(column_name='Tank', reverse=False, column_index=3))
        self.current_widget.heading(column='Damage', text='Damage', command=lambda: self.sort_table(column_name='Damage', reverse=False, column_index=4))
        self.current_widget.heading(column='Support', text='Support', command=lambda: self.sort_table(column_name='Support', reverse=False, column_index=5))
        self.current_widget.heading(column='Play time', text='Play time', command=lambda: self.sort_table(column_name='Play time', reverse=True, column_index=6))
        self.current_widget.heading(column='Win rate', text='Win rate', command=lambda: self.sort_table(column_name='Win rate', reverse=True, column_index=7))
        self.current_widget.heading(column='KD', text='KD', command=lambda: self.sort_table(column_name='KD', reverse=True, column_index=8))
        self.current_widget.pack(fill='both', expand=True)

        # set colors for certain tags
        self.current_widget.tag_configure(tagname='Limited', background='#460000')
        self.current_widget.tag_configure(tagname='Private', background='#460000')

    def sort_table(self, column_index, column_name, reverse):
        """Sorting table in order."""

        # global variable
        data = []
        play_time = False

        # get own order for: status, season, role
        if column_name in ['Status', 'Season', 'Tank', 'Damage', 'Support']:
            order = None

            # for status
            if column_name == 'Status':
                order = {"Public": 0, "Limited": 1, "Private": 2}

            # for season
            elif column_name == 'Season':
                order = {str(i): i for i in range(1, 100)}

            # for role
            elif column_name in ['Tank', 'Damage', 'Support']:
                order = {"Bronze-5": 0, "Bronze-4": 1, "Bronze-3": 2, "Bronze-2": 3, "Bronze-1": 4,
                         "Silver-5": 5, "Silver-4": 6, "Silver-3": 7, "Silver-2": 8, "Silver-1": 9,
                         "Gold-5": 10, "Gold-4": 11, "Gold-3": 12, "Gold-2": 13, "Gold-1": 14,
                         "Platinum-5": 15, "Platinum-4": 16, "Platinum-3": 17, "Platinum-2": 18, "Platinum-1": 19,
                         "Diamond-5": 20, "Diamond-4": 21, "Diamond-3": 22, "Diamond-2": 23, "Diamond-1": 24,
                         "Master-5": 25, "Master-4": 26, "Master-3": 27, "Master-2": 28, "Master-1": 29,
                         "Grandmaster-5": 30, "Grandmaster-4": 31, "Grandmaster-3": 32, "Grandmaster-2": 33, "Grandmaster-1": 34}

            # get own data for this
            data = [(order.get(self.current_widget.item(child, "values")[column_index], float('-inf')), child) for child in self.current_widget.get_children('')]

        # get data for nickname
        elif column_name == 'Nickname':
            data = [(self.current_widget.item(child, "values")[column_index].lower(), child) for child in self.current_widget.get_children('')]

        # get data for play time
        elif column_name == 'Play time':
            play_time = True
            for child in self.current_widget.get_children(''):
                play_time_str = self.current_widget.item(child, "values")[column_index]
                if play_time_str == '-':
                    data.append(((), child))
                else:
                    hours, minutes = play_time_str.split('hr')
                    hours = int(hours.strip())
                    minutes = int(minutes.replace('min', '').strip())
                    data.append(((hours, minutes), child))

        # get data for win rate | need to rename
        elif column_name == 'Win rate':
            data = [(float(self.current_widget.item(child, "values")[column_index].replace('%', '')), child)
                    if self.current_widget.item(child, "values")[column_index] != '-' else (float('-inf'), child) for child in self.current_widget.get_children('')]

        # get data for KD | need to rename
        elif column_name == 'KD':
            data = [(float(self.current_widget.item(child, "values")[column_index])
                     if self.current_widget.item(child, "values")[column_index] != '-' else float('-inf'), child) for child in self.current_widget.get_children('')]

        # another sort
        data.sort(reverse=reverse)
        if not reverse:
            if play_time:
                data.sort(key=lambda x: (x[0][0], -x[0][1]) if x[0] != () else (float('inf'), 0))
            else:
                data.sort(key=lambda x: x[0] if x[0] != float('-inf') else float('inf'))

        # update widget
        for ind, (_, child) in enumerate(data):
            self.current_widget.move(child, '', ind)
        self.current_widget.heading(column_name, command=lambda: self.sort_table(column_name=column_name, reverse=not reverse, column_index=column_index))
