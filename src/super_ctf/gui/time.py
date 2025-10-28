import tkinter as tk
from . import CanvasSettings
from .confetti import ConffetiAnimation


class Countdown:
    def __init__(self, seconds_to_count: int):
        self.time: int = seconds_to_count
        self.remaining_time: int = self.time
        
        self.window = tk.Tk()
        self.window.geometry(f"{CanvasSettings.WIDTH}x{CanvasSettings.HEIGHT}")
        self.window.resizable(False, False)
        self.window.configure(bg=CanvasSettings.BG_COLOR)

        self.timer_label = tk.Label(
            self.window, text="", font=("Digital-7", 80), fg="#07f017", bg=CanvasSettings.BG_COLOR
        ) # NOTE: Digital-7 needed to be downloaded
        self.timer_label.pack(pady=30)

        self.conffeti = ConffetiAnimation(self.window)

    def _update_display(self, current_time: int):
        mins, secs = divmod(self.remaining_time, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.timer_label.config(text=time_str)

    def _count(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self._update_display(self.remaining_time)
            self.window.after(1000, self._count)
        else:
            self._update_display(0)
            self.timer_label.config(foreground="#ff5e5e")
            
            # TODO: change to where needed
            tk.Widget.lift(self.conffeti.canvas)
            self.conffeti.start()
            self.timer_label.destroy()

    def start(self):
        self._update_display(self.remaining_time)
        self.window.after(1000, self._count)
        self.window.mainloop()
