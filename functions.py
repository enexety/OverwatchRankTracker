from tkinter import ttk


def add_information_text_widget(text_widget):
    """if file with battle-tags exist > add this battle-tags in text-widget
       if file with battle-tags not exist > it is ignored"""

    # add battle tags in text-widget
    try:
        with open('saved_battle_tags.json', 'r') as f:
            data = f.read().strip()
            if data:
                text_widget.insert('1.0', data)

    # when file not exist
    except FileNotFoundError:
        pass


def create_scrollbar(frame, widget):
    """It creates scrollbar"""
    scrollbar = ttk.Scrollbar(frame, command=widget.yview)
    scrollbar.pack(side='right', fill='y', pady=10)
    widget.config(yscrollcommand=scrollbar.set)
