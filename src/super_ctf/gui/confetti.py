import random
import tkinter as tk
import math
from typing import Tuple

from . import CanvasSettings

# Brighter, varied palette
POSSIBLE_COLORS: list[str] = [
    "#FFD700",  # gold
    "#FF6B6B",  # coral
    "#4D96FF",  # sky
    "#6BFFB8",  # mint
    "#FFCF6B",  # warm
    "#C86BFF",  # purple
    "#FF6BC8",  # pink
    "#6BFFEA",  # cyan
    "#FFFFFF",  # white
]

# Tweakable physics / appearance
BURST_SPEED: int = 12
GRAVITY = 0.32
CONFETTI_COUNT: int = 260
ROTATION_MAX = 8.0
WIND_FORCE = 0.6  # gentle horizontal drift over time
SPARKLE_CHANCE = 0.08
FADE_START = 220
TOTAL_FRAMES = 350


def _hex_fade(hex_color: str, factor: float) -> str:
    # factor in [0,1]
    if not hex_color.startswith("#") or len(hex_color) != 7:
        return hex_color
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


class Particle:
    """A single confetti particle (rectangle or circle)."""

    def __init__(self, canvas: tk.Canvas, x: float, y: float):
        self.canvas = canvas
        self.shape = random.choice(("rect", "oval"))
        self.color = random.choice(POSSIBLE_COLORS)
        self.size = random.uniform(5, 14)

        # Start position
        self.x = x
        self.y = y

        # Velocities
        self.vx = random.uniform(-BURST_SPEED, BURST_SPEED) * 0.6
        self.vy = random.uniform(1, BURST_SPEED)

        # Angular rotation (for rects)
        self.angle = random.uniform(0, 360)
        self.avel = random.uniform(-ROTATION_MAX, ROTATION_MAX)

        # Lifetime frames
        self.age = 0

        # Draw
        if self.shape == "rect":
            self.id = self._create_rect(self.x, self.y)
        else:
            self.id = self.canvas.create_oval(
                self.x, self.y, self.x + self.size, self.y + self.size, fill=self.color, outline=""
            )

    def _create_rect(self, x: float, y: float) -> int:
        w = self.size * 1.4
        h = self.size * 0.8
        # points centered at x,y
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
        coords = self._rotated_points(x + self.size / 2, y + self.size / 2, pts, self.angle)
        return self.canvas.create_polygon(coords, fill=self.color, outline="")

    def _rotated_points(self, cx: float, cy: float, pts: list[Tuple[float, float]], angle: float) -> list[float]:
        rad = math.radians(angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        out: list[float] = []
        for px, py in pts:
            rx = px * cos_a - py * sin_a + cx
            ry = px * sin_a + py * cos_a + cy
            out.extend([rx, ry])
        return out

    def update(self, frame: int) -> None:
        # Apply physics
        self.vy += GRAVITY
        # gentle wind that changes a bit with time
        self.vx += math.sin((self.age + frame) * 0.02) * (WIND_FORCE * 0.02)

        self.canvas.move(self.id, self.vx, self.vy)
        self.age += 1

        # Rotate rectangles by recomputing polygon points
        if self.shape == "rect":
            self.angle += self.avel
            # get current bbox center to compute rotation around center
            coords = self.canvas.coords(self.id)
            if len(coords) >= 2:
                cx = sum(coords[::2]) / (len(coords) // 2)
                cy = sum(coords[1::2]) / (len(coords) // 2)
            else:
                cx, cy = self.x, self.y
            # recompute rotated points
            w = self.size * 1.4
            h = self.size * 0.8
            pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
            new_coords = self._rotated_points(cx, cy, pts, self.angle)
            try:
                self.canvas.coords(self.id, *new_coords)
            except tk.TclError:
                # item might be deleted
                pass

        # occasional sparkles for small visual punch
        if random.random() < SPARKLE_CHANCE:
            try:
                bx = self.canvas.bbox(self.id)
                if bx:
                    sx = (bx[0] + bx[2]) / 2
                    sy = (bx[1] + bx[3]) / 2
                    sz = max(1.0, self.size * 0.2)
                    sparkle = self.canvas.create_oval(sx - sz, sy - sz, sx + sz, sy + sz, fill="#FFFFFF", outline="")
                    # remove sparkle shortly
                    self.canvas.after(90, lambda i=sparkle: self.canvas.delete(i))
            except tk.TclError:
                pass

    def fade(self, factor: float) -> None:
        try:
            newc = _hex_fade(self.color, factor)
            self.canvas.itemconfig(self.id, fill=newc)
        except tk.TclError:
            pass


class ConffetiAnimation:
    def __init__(
        self,
        parent_app: tk.Tk,
        width: int = CanvasSettings.WIDTH,
        height: int = CanvasSettings.HEIGHT,
        confetti_count: int = CONFETTI_COUNT,
    ) -> None:
        self.parent_app: tk.Tk = parent_app
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(parent_app, width=width, height=height, bg=CanvasSettings.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        tk.Widget.lift(self.canvas)

        self.confetti_count = confetti_count
        self.particles: list[Particle] = []
        self.running = False
        self.frame = 0
        # Ensure the animation runs only once unless explicitly reset
        self.played_once = False

    def _get_size(self) -> Tuple[int, int]:
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width() or self.width
        h = self.canvas.winfo_height() or self.height
        return w, h

    def create(self) -> None:
        # Emit across the full width from near the top so confetti fills the whole screen
        w, h = self._get_size()
        self.particles = []
        for _ in range(self.confetti_count):
            x = random.uniform(0, w)
            y = random.uniform(-40, 30)  # slightly above the visible area
            p = Particle(self.canvas, x, y)
            self.particles.append(p)
        self.frame = 0

    def animate(self, frames: int = TOTAL_FRAMES) -> None:
        if not self.running:
            return

        for p in list(self.particles):
            p.update(self.frame)

        # start fading near the end
        if self.frame >= FADE_START:
            fade_factor = max(0.0, 1.0 - (self.frame - FADE_START) / max(1, (TOTAL_FRAMES - FADE_START)))
            for p in self.particles:
                p.fade(fade_factor)

        self.frame += 1

        if frames > 0:
            self.parent_app.after(20, lambda: self.animate(frames - 1))
        else:
            self.running = False
            # cleanup
            for p in self.particles:
                try:
                    self.canvas.delete(p.id)
                except Exception:
                    pass
            self.particles = []
            # mark that we've played once
            self.played_once = True

    def start(self) -> None:
        # ensure canvas fills parent and then emit across it
        self.canvas.update_idletasks()
        # if we've already played once, don't start again
        if self.played_once:
            return

        # prevent double-start while running
        if self.running:
            return

        self.create()
        self.running = True
        self.animate()

    def reset(self) -> None:
        """Allow the animation to be played again."""
        # cleanup any remaining particles
        for p in list(self.particles):
            try:
                self.canvas.delete(p.id)
            except Exception:
                pass
        self.particles = []
        self.played_once = False
