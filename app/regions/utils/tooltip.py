import tkinter as tk

class ToolTip:
    """
    Create a tooltip for a given widget
    """
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
        self.scheduled = None
        
    def on_enter(self, event=None):
        self.schedule_tooltip()
        
    def on_leave(self, event=None):
        self.cancel_tooltip()
        self.hide_tooltip()
        
    def on_motion(self, event=None):
        self.cancel_tooltip()
        self.hide_tooltip()
        self.schedule_tooltip()
        
    def schedule_tooltip(self):
        self.cancel_tooltip()
        self.scheduled = self.widget.after(self.delay, self.show_tooltip)
        
    def cancel_tooltip(self):
        if self.scheduled:
            self.widget.after_cancel(self.scheduled)
            self.scheduled = None
            
    def show_tooltip(self):
        if self.tooltip_window or not self.text:
            return
            
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background="#ffffe0", relief='solid', borderwidth=1,
                        font=("Arial", "9", "normal"), wraplength=300)
        label.pack()
        
    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None