import base64
import tkinter
from tkinter import ttk

import ButtonManager
import WidgetManager
import FileManager


class MainWindow:

    def __init__(self, logManager=None):
        self.logManager = logManager
        self.main_window = None
        self.widgetManager = None
        self.fileManager = None

    def run(self):
        """Start the main window and create everything you need on it: frames, buttons, widgets, custom closing."""

        # configure window
        self.create_and_configure_window()

        # set settings
        self.fileManager = FileManager.FileManager()
        self.fileManager.set_settings()

        # set frame and widgets
        self.widgetManager = WidgetManager.WidgetManager()
        self.widgetManager.set_widget_frame(main_window=self.main_window)
        self.widgetManager.create_text_widget(fileManager=self.fileManager)

        # set frame and buttons
        buttonManager = ButtonManager.ButtonManager(mainWindow=self, widgetManager=self.widgetManager)
        buttonManager.set_button_frame()
        buttonManager.set_buttons()

        # custom close
        self.main_window.protocol("WM_DELETE_WINDOW", lambda: buttonManager.click_exit_button())

        # launch window
        self.main_window.mainloop()

    def create_and_configure_window(self):
        """Create: main window, title, style, centering, logo."""

        # create
        self.main_window = tkinter.Tk()
        self.main_window.title('Overwatch Rank Tracker')

        # set style
        style = ttk.Style(self.main_window)
        style.theme_use("clam")
        style.configure('Treeview', background='#2B2B2B', foreground="white", fieldbackground="#2B2B2B")

        # set size
        window_width = 800
        window_height = 600
        self.main_window.minsize(window_width, window_height)

        # center window
        self.center_window(window=self.main_window, window_width=window_width, window_height=window_height)

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
        logo_image = tkinter.PhotoImage(data=base64.b64decode(logo_base64.split(",")[1]))
        self.main_window.iconphoto(True, logo_image)

    @staticmethod
    def center_window(window, window_width, window_height):
        """Window centering."""

        # display sizing
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # calculate the x and y coordinates to center the window on the screen
        x_cord = int((screen_width / 2) - (window_width / 2))
        y_cord = int((screen_height / 2) - (window_height / 2))

        # set the window's geometry to center it on the screen
        window.geometry(f"{window_width}x{window_height}+{x_cord}+{y_cord}")
