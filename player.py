from pygame import Vector2, Vector3, draw, display, Color, time, math
from gameObject import GameObject

class Player(GameObject):
    def __init__(self, screen: display, pos: Vector3, coords,
                 colour: Color=GameObject.BLACK, active=True, velocity=Vector2(0,0)) -> None:
        super().__init__(screen, pos, colour, active, velocity)
        self.trail = [coords.copy()]

    def draw(self, pos) -> None:
        draw.circle(self.screen, self.colour, pos, 10)
        # self.draw_trail()

    def move(self, location: Vector3, coords) -> None:
        self.pos = location
        self.trail.append(coords.copy())

    def draw_trail(self, screen) -> None:
        length = len(self.trail)
        if length > 1:
            for i in range(length-1):
                lerp_float = i/length
                if lerp_float < 0.5:
                    colour = Color("red")

                elif lerp_float < 0.7:
                    colour = Color("red").lerp(
                        "yellow", (lerp_float-0.5)/0.2)
                else:
                    colour = Color(255,255,0,255).lerp(
                        "white", (lerp_float-0.7)/0.3)
                draw.line(screen, colour, self.trail[i],
                          self.trail[i+1], 4)
    def reset_trail(self, coords) -> None:
        self.trail = [coords.copy()]


class Goal(GameObject):
    def __init__(self, screen: display, pos: Vector2,
                 colour: Color=GameObject.BLACK, active=True, velocity=Vector3(0,0,0)) -> None:
        super().__init__(screen, pos, colour, active, velocity)

    def draw(self, pos) -> None:
        draw.circle(self.screen, self.colour, pos, 5)