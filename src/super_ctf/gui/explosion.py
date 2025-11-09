"""A dramatic full-screen explosion animation for the failure state.

Usage:
    from super_ctf.gui.explosion import ExplosionAnimation
    anim = ExplosionAnimation(root)
    anim.trigger()

This implementation uses a Canvas and simple particle system to create a
flash-and-debris effect. It's intentionally lightweight and pure-Tkinter so it
works without external dependencies.
"""

from __future__ import annotations

import contextlib
import random
import tkinter as tk

from super_ctf.gui import CanvasSettings


class _Debris:
    def __init__(self, canvas: tk.Canvas, x: float, y: float) -> None:
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = random.uniform(-12, 12)
        self.vy = random.uniform(-12, 12)
        self.size = random.uniform(2.5, 8.0)
        self.rotation = random.uniform(0, 360)
        self.color = random.choice(["#222222", "#444444", "#111111", "#ff5500"])
        self.id = canvas.create_rectangle(
            x, y, x + self.size, y + self.size, fill=self.color, outline=""
        )

    def update(self) -> None:
        self.vy += 0.6  # gravity
        self.x += self.vx
        self.y += self.vy
        self.canvas.move(self.id, self.vx, self.vy)


class ExplosionAnimation:
    def __init__(self, parent: tk.Tk | tk.Toplevel):
        self.parent = parent
        self.width = CanvasSettings.WIDTH
        self.height = CanvasSettings.HEIGHT

        self.canvas = tk.Canvas(
            parent,
            width=self.width,
            height=self.height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.place(x=0, y=0)
        self.debris: list[_Debris] = []
        self.running = False

    def _center(self) -> tuple[float, float]:
        self.canvas.update_idletasks()
        return (self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2)

    def _flash(self) -> None:
        # brief fullscreen flash
        rect = self.canvas.create_rectangle(0, 0, self.width, self.height, fill="white")
        self.parent.after(80, lambda: self.canvas.delete(rect))

    def _spawn_debris(self, count: int = 120) -> None:
        cx, cy = self._center()
        self.debris = [
            _Debris(
                self.canvas, cx + random.uniform(-10, 10), cy + random.uniform(-10, 10)
            )
            for _ in range(count)
        ]

    def _update(self, frames: int = 200) -> None:
        if frames <= 0:
            self.running = False
            return

        for d in list(self.debris):
            d.update()
            # fade tiny pieces by shrinking
            if d.y > self.height + 50 or d.x < -50 or d.x > self.width + 50:
                with contextlib.suppress(Exception):
                    self.canvas.delete(d.id)
                with contextlib.suppress(ValueError):
                    self.debris.remove(d)

        # schedule next frame
        self.parent.after(24, lambda: self._update(frames - 1))

    def trigger(self, debris: int = 160) -> None:
        if self.running:
            return
        self.running = True
        # flash then spawn debris
        self._flash()
        self._spawn_debris(count=debris)
        self._update()


class ExplosionOverlay:
    """A convenience overlay window that covers the parent and runs the
    explosion animation. The overlay is a transient Toplevel that will be
    destroyed after the animation finishes.
    """

    def __init__(self, parent: tk.Tk | tk.Toplevel):
        self.parent = parent
        # Create a fullscreen/parent-covering Toplevel
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        # place over the parent window
        try:
            x = parent.winfo_rootx()
            y = parent.winfo_rooty()
            w = parent.winfo_width()
            h = parent.winfo_height()
        except Exception:
            x = y = 0
            w = CanvasSettings.WIDTH
            h = CanvasSettings.HEIGHT

        self.win.geometry(f"{w}x{h}+{x}+{y}")
        self.win.configure(bg="black")

        self.anim = ExplosionAnimation(self.win)

    def trigger(self, debris: int = 160, duration_ms: int = 6000) -> None:
        # Play animation and schedule destroy
        self.anim.trigger(debris=debris)

        # Destroy overlay after duration
        self.win.after(duration_ms, self.win.destroy)


__all__ = ["ExplosionAnimation", "ExplosionOverlay"]
