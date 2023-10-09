import tkinter


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, _event):
        """Creates a tooltip for the widget."""

        # get coordinates to display the tooltip next to the widget
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # create a pop-up window for the tooltip
        self.tooltip = tkinter.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_attributes('-topmost', 1)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        # create a label to display the tooltip text
        label = tkinter.Label(self.tooltip, text=self.text, background="lightyellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, _event):
        """Hides the tooltip for the widget."""

        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
