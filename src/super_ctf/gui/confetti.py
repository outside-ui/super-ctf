import random
from . import CanvasSettings

POSSIBLE_COLORS: List[str] = [
                                "red",
                                "yellow",
                                "blue",
                                "green",
                                "purple",
                                "orange",
                                "pink",
                                "white",
                                "cyan",
                            ]
BURST_SPEED: int = 8
GRAVITY = 0.38
CONFFETI_COUNT: int = 250


class ConfettiDot:
    def __init__(self, canvas: tk.Canvas, cx: float, cy: float):
        self.canvas = canvas
        self.color: str = random.choice(POSSIBLE_COLORS)
        self.x = cx + random.randint(-20, 20)
        self.y: int = cy + random.randint(-20, 20)
        self.size: int = random.randint(4, 10)
        self.vx: int = random.uniform(-BURST_SPEED, BURST_SPEED)
        self.vy: int = random.uniform(-BURST_SPEED, BURST_SPEED)
        self.id: int = canvas.create_oval(self.x, self.y, self.x+self.size, self.y+self.size, fill=self.color, outline="")

    def update(self):
        self.canvas.move(self.id, self.vx, self.vy)
        self.vy += GRAVITY


class ConffetiAnimation:
    def __init__(self, 
                parent_app: tk.Tk, 
                width: int = CanvasSettings.WIDTH, 
                height: int = CanvasSettings.HEIGHT, 
                conffeti_count: int = CONFFETI_COUNT
                ):
        self.parent_app: tk.Tk= parent_app
        
        self.width = width
        self.height = height 
        self.canvas = tk.Canvas(parent_app, width=width, height=height, bg=CanvasSettings.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        tk.Widget.lift(self.canvas)

        self.conffeti_count: int = conffeti_count
        self.conffeti: List[ConfettiDot] = []

        self.running = False
    
    def _get_center(self):
        self.canvas.update_idletasks()
        w = self.canvas.winfo_width() or self.width
        h = self.canvas.winfo_height() or self.height
        return w / 2, h / 2
    
    def create(self):
        cx, cy = self._get_center()
        self.conffeti = [ConfettiDot(self.canvas, cx, cy) for _ in range(self.conffeti_count)]

    def animate(self, frames: int = 350):
        frames = 350 # run that many frames (~20ms per frame)

        if not self.running:
            return

        for dot in self.conffeti:
            dot.update()

        if frames > 0:
            self.parent_app.after(20, lambda: self.animate(frames - 1))
        else:
            self.running = False

    def start(self):
        self.canvas.update_idletasks()
        self.create()
        self.running = True
        self.animate()