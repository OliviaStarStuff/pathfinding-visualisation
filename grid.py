import numpy as np

from math import cos,sin, pi
from pygame import Color, draw, Vector2, display, math, gfxdraw, Vector3, font
from random import randint

class Hex:
    def __init__(self, pos: Vector3, colour: Color, parent_pos = None) -> None:
        self.pos = pos
        self.colour = colour
        self.parent_pos = parent_pos
    def copy(self):
        return Hex(self.pos, self.colour)

class HexGrid:
    def __init__(self, cell_num: Vector2, center: Vector2,
                 colour: Color=Color(0,168,32), size: float=20, pointy=False, overlay=False) -> None:
        self.overlay=overlay
        self.pointy = pointy
        self.size = Vector2(size/2, (size/2)*cos(pi/6))
        self.unitVector = Vector2( self.size.x, 0).rotate(pointy*30)
        self.cell_num = cell_num
        self.colour = colour
        self.center = center
        self.start_pos = self.center - Vector2(self.cell_num.x * self.size.x * 3/4, self.cell_num.y*self.size.y)
        self.generate_cells()

    def get_size(self):
        return self.cell_num.y * self.cell_num.x

    def rotate(self, screen):
        self.pointy = not self.pointy
        self.unitVector = Vector2( self.size.x, 0).rotate(self.pointy*30)
        # self.start_pos = Vector2(-self.cell_num.x * self.size.y, -self.cell_num.y * self.size.x*2/3)+self.center
        self.generate_cells()

        self.draw(screen)

    def get_points(self) -> list[Vector2]:
        points = []
        for i in range(6):
            points.append(self.unitVector.rotate_rad(i*pi/3))
        return points

    def reset(self):
        for hex in self.cells:
            if hex is not None:
                hex.colour = self.colour
                hex.parent_pos = None

    def generate_cells(self):
        self.cells: list[Hex] = []
        for q in range(int(self.cell_num.x)):
            for j in range(int(self.cell_num.y)):
                r = j - q//2
                s = 0 - r - q
                cell = Hex(Vector3(q, r, s), self.colour)
                self.cells.append(cell)

    def pos_to_index(self, pos: Vector3):
        return int((pos.y+pos.x//2) + pos.x * self.cell_num.y)

    def index_to_pos(self, index):
        return self.cells[index]

    def random_pos(self):
        hex = None
        while hex is None:
            hex = self.cells[randint(0, len(self.cells)-1)]
        return hex.pos

    def draw(self, screen) -> None:
        for hex in self.cells:
            p2 = []
            if hex is not None:
                coords = self.pos_to_coords(hex.pos)
                for p in self.get_points():
                    p2.append(p + coords)
                gfxdraw.filled_polygon(screen, p2, hex.colour)
                draw.polygon(screen, Color("black").lerp(hex.colour, 0.8), p2, 1)
        if self.overlay:
            for hex in self.cells:
                if hex is not None and hex.parent_pos is not None and hex.colour != Color(168,0,168):
                    start_pos = self.pos_to_coords(hex.pos)
                    end_pos = self.pos_to_coords(hex.parent_pos)
                    draw.line(screen, (255, 255, 255), start_pos, end_pos)
                # gfxdraw.aapolygon(screen, p2, Color("black"))

    def set_parent(self, pos, parent_pos):
        self.cells[self.pos_to_index(pos)].parent_pos = parent_pos

    def pos_to_coords(self, pos):
        # q = x, y = r, z = s
        x = pos.x * self.size.x * 1.5
        y = -pos.x * self.size.y
        y += (pos.x + pos.y) * self.size.y * 2
        if self.pointy:
            return Vector2(y, x) + self.start_pos
        else:
            return Vector2(x, y) + self.start_pos

    def copy(self):
        return [cell.copy() if cell is not None else None for cell in self.cells]

    def coords_to_pos(self, coords: Vector2):
        c2 = coords - self.start_pos
        x, y = (c2.y, c2.x) if self.pointy else (c2.x, c2.y)

        x /= self.size.x * 1.5
        x = round(x)
        y += x * self.size.y
        y /= self.size.y * 2
        y = round(y)
        y -= x
        return Vector3(x, y, 0-x-y)

    def set_highlight(self, pos: Vector3, colour = Color(168,0,168)):
        if self.is_valid_pos(pos):
            self.cells[self.pos_to_index(pos)].colour = colour
        else:
            print("not valid", pos)

    def get_cell(self, pos):
        return self.cells[self.pos_to_index(pos)]

    def clear_cell(self, pos):
        self.cells[self.pos_to_index(pos)] = None

    def new_cell(self, pos):
        cell = Hex(pos, self.colour)
        self.cells[self.pos_to_index(pos)] = cell

    def move(self, direction, coords):

        result = self.coords_to_pos(coords)
        print(result, result - direction, result.x, result.y, result.z)
        if not self.is_valid_pos(result-direction):
            return coords
        return self.pos_to_coords(result - direction)

    def get_neighbours(self, pos) -> list[Vector3]:
        neighbours = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if i != j or j != k:
                        if (self.is_valid_pos(pos + Vector3(i, j, k))):
                            neighbours.append(pos + Vector3(i, j, k))
        return neighbours

    def generate_walls(self, number_of_walls, goal_pos, player_pos=Vector2(0,0)):
        for i in range(number_of_walls):
            random_pos = self.random_pos()
            while not self.is_valid_pos(random_pos) and random_pos != goal_pos and random_pos != player_pos:
                random_pos = self.random_pos()
            index = self.pos_to_index(random_pos)
            if self.cells[index].pos != self.coords_to_pos(self.start_pos) \
            and self.cells[index].pos != goal_pos:
                self.cells[index] = None

    def is_valid_pos(self, pos) -> bool:
        if pos.x + pos.y + pos.z != 0:
            return False
        if pos.x < 0 or  pos.x >= self.cell_num.x:
            return False
        if pos.z > pos.y:
            return False
        if -(pos.x//2) > pos.y or self.cell_num.y-(pos.x//2) <= pos.y:
            return False
        if self.pos_to_index(pos) >= len(self.cells):
            return False
        if self.cells[self.pos_to_index(pos)] is None:
            return False
        return True

    def estimate_remaining_cost(self, pos_1: Vector2, pos_2: Vector2):
        d_pos = pos_1 - pos_2
        distance = 0
        for i in d_pos[:]:
            if i > 0:
                distance += i
        return distance
        distance: Vector2 = self.pos_to_coords(pos_1) - self.pos_to_coords(pos_2)
        distance.x /= self.size.x
        distance.y /= self.size.y
        return distance.magnitude_squared()

    def draw_trail(self, screen, pos):
        p2 = []
        for p in self.get_points():
            p2.append(p + self.pos_to_coords(pos))
        gfxdraw.filled_polygon(screen, p2, Color('orange'))

def main() -> None:
    from pygame import time, event, QUIT
    import pygame as pg
    from player import Player
    # grid = SquareGrid(10, 20, Vector2(50, 50))
    screen = display.set_mode((1280, 720))
    grid = HexGrid(3, 3, Vector2(screen.get_width(), screen.get_height())/2, size=120.0, pointy=False)

    grid.draw(screen)
    clock = time.Clock()
    running = True
    pos = grid.random_pos()
    player = Player(screen, pos, grid.pos_to_coords(pos), Color("red"))
    interval = 200
    lastTime = {pg.K_w:0, pg.K_s:0, pg.K_a:0, pg.K_d:0,
                        pg.K_e:0, pg.K_q:0, pg.K_r:0, pg.K_p:0}
    pg.init()
    while running:
        screen.fill("black")
        for e in event.get():
            if e.type == QUIT:
                running = False

        grid.draw(screen)
        myfont = font.Font('freesansbold.ttf', 12)
        # for i in grid.cells:
        # # render text
        #     text = myfont.render(str(i.pos), 1, (255,255,0))
        #     screen.blit(text, grid.pos_to_coords(i.pos)-grid.size)

        # text = myfont.render(str(grid.coords_to_pos(player.pos)), 1, (255,0,0))
        # screen.blit(text, grid.pos_to_coords(grid.coords_to_pos(player.pos))-grid.size)

        for v in grid.get_points():
            # draw.circle(screen, "red", v + player.pos, 5)
            text = myfont.render(str(player.trail[0] + v), 1, (255,0,0))
            screen.blit(text, player.trail[0])
        coords = grid.pos_to_coords(player.pos)
        keys = pg.key.get_pressed()
        if keys[pg.K_w] and pg.time.get_ticks() > interval + lastTime[pg.K_w]:
            lastTime[pg.K_w] = pg.time.get_ticks()
            player.move(grid.move([1, 0, -1], coords),coords)
            grid.set_highlight(player.pos)
        if keys[pg.K_s] and pg.time.get_ticks() > interval + lastTime[pg.K_s]:
            lastTime[pg.K_s] = pg.time.get_ticks()
            player.move(grid.move([-1, 0, 1], coords),coords)
            grid.set_highlight(player.pos)
        if keys[pg.K_d] and pg.time.get_ticks() > interval + lastTime[pg.K_d]:
            lastTime[pg.K_d] = pg.time.get_ticks()
            player.move(grid.move([0,-1,1], coords),coords)
            grid.set_highlight(player.pos)
        if keys[pg.K_q] and pg.time.get_ticks() > interval + lastTime[pg.K_q]:
            lastTime[pg.K_q] = pg.time.get_ticks()
            player.move(grid.move([0,1,-1], coords),coords)
            grid.set_highlight(player.pos)
        if keys[pg.K_e] and pg.time.get_ticks() > interval + lastTime[pg.K_e]:
            lastTime[pg.K_e] = pg.time.get_ticks()
            player.move(grid.move([1,-1,0], coords),coords)
            grid.set_highlight(player.pos)
        if keys[pg.K_a] and pg.time.get_ticks() > interval + lastTime[pg.K_a]:
            lastTime[pg.K_a] = pg.time.get_ticks()
            player.move(grid.move([-1,1, 0], coords),coords)
            grid.set_highlight(player.pos)
        if keys[pg.K_r] and pg.time.get_ticks() > interval + lastTime[pg.K_r]:
            lastTime[pg.K_r] = pg.time.get_ticks()
            screen.fill("Black")
            grid.rotate(screen)

        player.draw(coords),coords
        display.flip()
        dt = clock.tick(60) / 1000

if __name__ == "__main__":
    main()