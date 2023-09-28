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

    def create_table_widget(self):
        """Create table-widget. Columns = 9, full length for 800x600 = 796."""

        # set table
        self.current_widget = ttk.Treeview(self.widget_frame, columns=['Status', 'Nickname', 'Season', 'Tank', 'Damage', 'Support', 'Play time', 'Win rate', 'KD'], show='headings', height=26)

        # set parameters
        self.current_widget.column('Status', minwidth=47, width=63, anchor='center', stretch=True)
        self.current_widget.column('Nickname', minwidth=134, width=156, anchor='center', stretch=True)
        self.current_widget.column('Season', minwidth=35, width=57, anchor='center', stretch=True)
        self.current_widget.column('Tank', minwidth=87, width=100, anchor='center', stretch=True)
        self.current_widget.column('Damage', minwidth=87, width=100, anchor='center', stretch=True)
        self.current_widget.column('Support', minwidth=87, width=100, anchor='center', stretch=True)
        self.current_widget.column('Play time', minwidth=72, width=91, anchor='center', stretch=True)
        self.current_widget.column('Win rate', minwidth=54, width=73, anchor='center', stretch=True)
        self.current_widget.column('KD', minwidth=37, width=56, anchor='center', stretch=True)

        # push table and columns
        self.current_widget.heading('Status', text='Status')
        self.current_widget.heading('Nickname', text='Nickname')
        self.current_widget.heading('Season', text='Season')
        self.current_widget.heading('Tank', text='Tank')
        self.current_widget.heading('Damage', text='Damage')
        self.current_widget.heading('Support', text='Support')
        self.current_widget.heading('Play time', text='Play time')
        self.current_widget.heading('Win rate', text='Win rate')
        self.current_widget.heading('KD', text='KD')
        self.current_widget.pack(fill='both', expand=True)

        # set colors for certain tags
        self.current_widget.tag_configure(tagname='Limited', background='#460000')
        self.current_widget.tag_configure(tagname='Private', background='#460000')

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

    def create_loading_text(self):
        """Adds the text "Loading..." to the widget_frame."""

        label = tkinter.Label(self.widget_frame, text='Loading...', font=('Calibri', 13, 'bold'), fg='#A0A0A0', bg="#2B2B2B")
        label.place(relx=0.5, rely=0.5, anchor='center')

    def create_scrollbar(self, widget, frame):
        """Creating a scrollbar or reverting it back."""

        # create a scrollbar if not previously created
        if not self.scrollbar:
            self.scrollbar = ttk.Scrollbar(frame, command=widget.yview)

        # insert into the widget and bind it to it
        self.scrollbar.pack(side='right', fill='y', pady=10)
        widget.config(yscrollcommand=self.scrollbar.set)
