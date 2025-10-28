from enum import Enum


class ConfettiSettings(Enum):
    CONFETTI_COUNT = 200
    GRAVITY = 0.3
    FRICTION = 0.98
    BURST_SPEED = 10
    COLORS = [
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


class CanvasSettings(Enum):
    HEIGHT = 200
    WIDTH = 400
