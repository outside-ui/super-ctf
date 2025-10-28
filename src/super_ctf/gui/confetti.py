import tkinter as tk
from typing import List
import random
import math
from config import CanvasSettings, ConfettiSettings

class ConfettiDot:
    def __init__(self, canvas: tk.Tk, x: int, y: int):
        self.__canvas = canvas
        self.__x = x
        self.__y = y
        self.__size = random.randint(4, 10)
        self.__color = random.choice(ConfettiSettings.COLORS.value)
        self.__vx = random.uniform(-ConfettiSettings.BURST_SPEED.value, ConfettiSettings.BURST_SPEED.value)
        self.__vy = random.uniform(-ConfettiSettings.BURST_SPEED.value, ConfettiSettings.BURST_SPEED.value)
        self.__shape = canvas.create_oval(
            x, y, x + self.__size, y + self.__size, fill=self.__color, outline=""
        )

    def update(self):
        # Apply motion and gravity
        self.__vy += ConfettiSettings.GRAVITY.value
        self.__vx *= ConfettiSettings.FRICTION.value
        self.__vy *= ConfettiSettings.FRICTION.value

        self.__x += self.__vx
        self.__y += self.__vy

        # Reset if it falls off screen
        if self.__y > CanvasSettings.HEIGHT.value:
            self.__y = random.randint(-50, 0)
            self.__vy = random.uniform(-5, -1)
            self.__vx = random.uniform(-2, 2)

        self.__canvas.move(self.__shape, self.__vx, self.__vy)

class ConfettiOverlay:
    def __init__(self, parent_root: tk.Tk):
        self.__overlay = tk.Toplevel(parent_root)
        self.__overlay.overrideredirect(True)
        self.__overlay.attributes("-topmost", True)
        self.__overlay.attributes("-transparentcolor", "grey")
        geometry = f"{CanvasSettings.WIDTH.value}x{CanvasSettings.HEIGHT.value}+{parent_root.winfo_rootx()}+{parent_root.winfo_rooty()}"
        self.__overlay.geometry(geometry)
        
        self.__canvas = tk.Canvas(self.__overlay, bg="grey", highlightthickness=0)
        self.__canvas.pack(fill="both", expand=True)

        self.__confetties = [] 
        self.animate()
        
        self.__parent_root = parent_root
        self.__parent_root.bind("<Configure>", self.__sync_position)

    def __sync_position(self, event=None):
        try:
            x = event.widget.winfo_rootx()
            y = event.widget.winfo_rooty()
            w = event.widget.winfo_width()
            h = event.widget.winfo_height()
            if w > 1 and h > 1:
                self.__overlay.geometry(f"{w}x{h}+{x}+{y}")
        except tk.TclError:
            pass

    def burst_confetti(self):
        self.__confetties = ConfettiOverlay.__create_confetti(self.__canvas)

    @staticmethod
    def __create_confetti(canvas):
        confetties: List[ConfettiDot] = []
        for _ in range(ConfettiSettings.CONFETTI_COUNT.value):
            confetties.append(ConfettiDot(canvas, CanvasSettings.WIDTH.value / 2, CanvasSettings.HEIGHT.value / 2))
        return confetties

    def animate(self):
        for c in self.__confetties:
            c.update()
        self.__overlay.after(20, self.animate)