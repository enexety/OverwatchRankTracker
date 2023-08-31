import base64
import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor

import functions


# global variables
version = "v0.0.4"
path_to_file = 'settings_and_battle_tags.json'

# personal information for GitHub Gist and e.t.c, used for sending logs
owner_name = 'enexety'
repo_name = 'Overwatch_Rank_Tracker'
token = ""


def main():

    # create main window
    window = tk.Tk()
    window.title('Overwatch Rank Tracker')
    window.geometry('800x600')
    window.configure(bg='#2B2B2B')
    window.minsize(800, 600)
    window.protocol("WM_DELETE_WINDOW", lambda: functions.exit_main_window(text_widget=text_widget, path=path_to_file))  # custom close

    # set style for window
    style = ttk.Style(window)
    style.theme_use("clam")
    style.configure('Treeview', background='#2B2B2B', foreground="white", fieldbackground="#2B2B2B")

    # set table
    table = ttk.Treeview(window, columns=['Status', 'Nickname', 'Season', 'Tank', 'Damage', 'Support', 'Play time', 'Win rate', 'KD'], show='headings', height=26)

    # set size and centering
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_cord = int((screen_width / 2) - (800 / 2))
    y_cord = int((screen_height / 2) - (600 / 2))
    window.geometry("{}x{}+{}+{}".format(800, 600, x_cord, y_cord))

    # set button_frame
    button_frame = tk.Frame(window, bg='#2B2B2B')
    button_frame.pack(side='bottom', fill='x')

    # set text_frame for text_widget
    text_frame = tk.Frame(window, bg="#2B2B2B")
    text_frame.pack(side="left", fill="both", expand=True)

    # loading text, it can be seen after clicking "Check"
    label = tk.Label(text_frame, text='Loading...', font=('Calibri', 13, 'bold'), fg='#A0A0A0', bg="#2B2B2B")
    label.place(relx=0.5, rely=0.5, anchor='center')

    # set buttons
    check_button = tk.Button(button_frame, text='Check', font=('Calibri', 17, 'bold'), pady=3, width=16,
                             command=lambda: ThreadPoolExecutor().submit(lambda: functions.check_button_click(check_button=check_button, save_button=save_button, text_frame=text_frame, table=table,
                                                                                                              text_widget=text_widget, path=path_to_file, owner_name=owner_name, token=token)))
    save_button = tk.Button(button_frame, text='Save', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: functions.save_button_click(text_widget=text_widget, path=path_to_file))
    settings_button = tk.Button(button_frame, text='Settings', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: functions.open_settings_window(window=window, path=path_to_file))
    exit_button = tk.Button(button_frame, text='Exit', font=('Calibri', 17, 'bold'), pady=3, width=16, command=lambda: functions.exit_main_window(text_widget=text_widget, path=path_to_file))
    check_button.pack(side='left', fill='x', expand=True)
    save_button.pack(side='left', fill='x', expand=True)
    settings_button.pack(side='left', fill='x', expand=True)
    exit_button.pack(side='left', fill='x', expand=True)

    # create text-widget
    text_widget = tk.Text(text_frame, font=('Calibri', 13, 'bold'), fg='#A0A0A0', insertbackground='white', padx=10, pady=15, bg="#2B2B2B", relief='flat')
    text_widget.pack(side='left', fill='both', expand=True)
    functions.add_information_text_widget(text_widget=text_widget, path=path_to_file)
    functions.create_scrollbar(frame=text_frame, widget=text_widget)

    # set logo image
    logo_base64 = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAFS0lEQVR4nO2ZwU4bRxjHv2+UqGnVCNNUaaQeME+AI4jUE15uJhecJ6g5EPUW5wl
    qngDnVsEhmyeIcwm+sXCqFFDgCTCHSilqiqu0FVWqnf7H9pod78zurHGFIvGTRvvNenfm++98883smukT51rAVXMtIOJs7dtSyB9XmLgkpSwSUQklziEzd6SkQNCN3emtXw5x7tJcSsDZD/eKYSifk
    KQqUc/pHHAHvbeE4GfTP73r0JiMJeCsXiyEf/29AbNGk4C5Kb74fH262emilovcAn5bu1djCpXzBZRJ0hVMq9Obpy3YzuQS8H7t7nMcavT/4t/ZOl3F0QlGceL3x9+8xOSswnSD6UhK7sJChMgC5sk
    cTCcw2Vtfbf76CGYmzgIGoaNGwAKfEEtfyJstW4YZZKoqSa5h0s+QBUli9eutdz45kClgYbHSYCFab4LXh2YRfCKJG64dRvTbkg24O0MxIucfeA9LMgyr+3vtBqWQKmDeW65SKF/isi7S3VJCBNOLO
    5unNboE7x/f9eH19zBxuHAe6XkHZwok+NFBsN3Cz0asAjyvWvgQ/nPca6SHLoKA6owmQLw9zfke3L0tPpsNglYXlQRWASp0JNGPMGNciEAlE/UQzum88HPQ7pADSef7wMl1WyjhtyTfeZXix5COYRr
    gZwd723UYqSx4FY9i7AftgDKYX1xuwvknMEfg7k0h75sehFGA+ekDppPbfKtkG84484sVnwX5pAipjidYhZWKGrEP8vyQJM2gqgFHjaOA80nmy5VjNFKkUTImVEQ0ghCwhCrJkHZuCpo1PcFRHniVW
    hjSc5g6TJ2D3fYsLA1G0ejHYfgWpg6ePhookgPRCMYFoAGn0FPgAXbIMApCiPuj849RNBa85boM5QZMDRb8dD/YbsLMBLF8RpiIIwJSs0mcPD4wigaeXksSrcDUMKk3EQ8BXYBqg1bfBG2fMrBGAdG
    Lg712jWIwigYEBJKoDFMDNyauNbFQXn6LPVMJZkIAejPGsQkkAYmDBhPtYiJ7FAPndEw34qojdNxzKg2VOofOgoQAoM45pdRyRWWjOZgxuIt5NA1jCKNomATgooRyE7jXJ+pvCxTKWRw0ASARBiZcI
    0GrKOCExEEDF2UKiMd+hEWA01wYX0C50iVJUzCH4KJUASbnFTYBiiwR8bk0hOkPhHIB1hBG0XBVHmFzXpEmQJEmwjUScE4HAoxp1LSSpjmPlo+w7fAIYHsQUGJC9jGJsKVROPsKAqowh+Ccjusi4uJ
    8tGgN9jjOIlx9UCQE2NTjymEOz+N8RB4RmIfGvZhpMWWUBGiggwZmYGqoTnCgvM5HuIjAwdy+ZS/GKAkwDxoSmzGYI6ivDPrLxpAM5yOyRKAh3J/sA46uI/4bNALOJ4m2wzDdcHQ+IltEElMSURgFK
    OyjMEJO5yPyiICTxqevwG9mBh100MEUqmbGdD5i0EeAPuZQNYPFC30UbX1YBSguPqtYYPLR+FNb41kMBGxAQI1siPS3wFQBCrycNMn4oj0A6RUfvur7O69foebMwtLDFXy4asL5IlnJfotjlEywrPs
    U22UagRAhRZME7Y7m6gi1xuAFvxxyWE93vIfTrpVRnHASEQMfaCFCdmECLiQ2Zuk4Oa9wFqDIDKeJkB02cXIJUPQmtpQ+QmAK1cmBbINhq6VNWBO5BShU9vgzPK9Ll3XCATix/qW41Rwnm+He8VEr9
    r8h1SQjDRr2Tqlgb8OS/Bv4emdaYV25lIA4KsNIkh7WDY/w/xlElSCqH2YIDzh7CKuLvB4wcWDLVHmZmICr4lrAVfPJC/gPBrjvT9GaIggAAAAASUVORK5CYII="""
    logo_image = tk.PhotoImage(data=base64.b64decode(logo_base64.split(",")[1]))
    window.iconphoto(True, logo_image)

    functions.check_for_updates(owner_name=owner_name, repo_name=repo_name, current_version=version)

    # launch
    window.mainloop()


if __name__ == "__main__":
    main()
