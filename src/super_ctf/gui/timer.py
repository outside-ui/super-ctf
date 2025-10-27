import tkinter as tk
from tkinter import ttk
from typing import Tuple
# import time

class Countdown:
    def __init__(self, time: int):
        self.__time: int = time
        self.__remaining_time: int = time
        self.__is_running: bool = False
        self.__root, self.__timer_label = Countdown.__initialize_GUI()

    @staticmethod
    def __initialize_GUI() -> Tuple:
        root = tk.Tk()
        root.title("The hardest CTF EVERRRER")
        root.geometry("400x200")
        root.resizable(False, False)
        root.configure(bg="#000000")

        # Timer Label
        timer_label = tk.Label(root,
                            text="05:00",
                            font=("Digital-7", 80),
                            fg="#07f017",
                            bg="#000000")
        
        timer_label.pack(pady=30)

        return root, timer_label

    def __countdown(self):
        """
        """
        if self.__remaining_time > 0:
            self.__remaining_time -= 1
            self.__update_display(self.__remaining_time)
            self.__root.after(1000, self.__countdown)
        else:
            self.__update_display(0)
            self.__timer_label.config(foreground="#ff5e5e")

    def __update_display(self, current_time: int):
        """Updates the time display label."""
        mins, secs = divmod(self.__remaining_time, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.__timer_label.config(text=time_str)

    def start(self) -> None:
        self.__update_display(self.__remaining_time)
        self.__root.after(1000, self.__countdown)
        self.__root.mainloop()
    
Countdown(5 * 60).start()