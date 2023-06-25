from __future__ import annotations
from pygame import Color, Vector2, Vector3, display
from abc import ABC, abstractmethod


class GameObject(ABC):
    BLACK = Color("black")
    def __init__(self, screen: display,  pos: Vector3, colour: Color=BLACK,
                 active: bool=True, velocity=Vector2(0,0)) -> None:
        super().__init__()

        self.screen = screen
        self.pos = pos
        self.colour = colour
        self.active = active
        self.velocity = velocity

    @abstractmethod
    def draw(self):
        pass

    def same_pos(self, other: GameObject) -> bool:
        if self.pos == other.pos:
            return True
        return False
