from math import pi
from pygame import Color, draw, Vector2, display, gfxdraw, Vector3, font
from random import randint
from abc import ABC, abstractmethod
from math import cos


class Grid(ABC):
    def __init__(self, cell_num: Vector2, center: Vector2, cell,
                 colour: Color=Color(0,168,32), size: float=20, overlay=False) -> None:
        self.overlay=overlay
        self.size = size
        self.cell_num = cell_num
        self.colour = colour
        self.center = center
        self.cell = cell
        self.start_pos = self.get_start_pos()
        self.generate_cells()

    def get_start_pos(self):
        return self.center - self.size.elementwise() * self.cell_num/2

    def generate_cells(self):
        self.cells = []
        for i in range(int(self.cell_num.x)):
            col = []
            for j in range(int(self.cell_num.y)):
                col.append(self.cell.make_cell(i, j, self.size, self.colour))
            self.cells.append(col)

    def generate_walls(self, number_of_walls, goal_pos, player_pos=Vector3(0,0,0)):
        for i in range(number_of_walls):
            random_pos = self.random_pos()
            while (not self.is_valid_pos(random_pos)) or random_pos == goal_pos or random_pos == player_pos:
                random_pos = self.random_pos()
            self.clear_cell(random_pos)

    def reset(self):
        for col in self.cells:
            for cell in col:
                if cell is not None:
                    cell.colour = self.colour
                    cell.parent_pos = None

    def get_size(self):
        return self.cell_num.y * self.cell_num.x

    @abstractmethod
    def get_neighbours(self, pos):
        pass

    def set_highlight(self, pos: Vector3, colour = Color(168,0,168)):
        if self.is_valid_pos(pos) and self.get_cell(pos) is not None:
            self.get_cell(pos).colour = colour
        else:
            print("not valid", pos)

    def set_parent(self, pos, parent_pos):
        self.get_cell(pos).parent_pos = parent_pos

    def copy(self):
        cells = []
        for cell_row in self.cells:
            new_cell_row = []
            for cell in cell_row:
                if cell is not None:
                    new_cell_row.append(cell.copy_cell())
                else:
                    new_cell_row.append(None)
            cells.append(new_cell_row)
        return cells

    @abstractmethod
    def estimate_remaining_cost(self, pos_1, pos_2) -> float:
        pass

    def random_pos(self):
        cell = None
        while cell is None:
            rand_x = randint(0, self.cell_num.x - 1)
            rand_y = randint(0, self.cell_num.y - 1)
            cell = self.cells[rand_x][rand_y]
        return cell

    @abstractmethod
    def is_valid_pos(self, pos) -> bool:
        pass

    @abstractmethod
    def pos_to_coords(self, pos):
        pass

    @abstractmethod
    def coords_to_pos(self, coords):
        pass

    def get_cell(self, index_pos):
        return self.cells[int(index_pos.x)][int(index_pos.y)]

    def clear_cell(self, pos):
        self.cells[int(pos.x)][int(pos.y)] = None

    def new_cell(self, pos):
        cell = self.cell(pos, self.size, self.colour)
        self.cells[int(pos.x)][int(pos.y)] = cell

    @abstractmethod
    def draw(self, screen) -> None:
        pass

    @abstractmethod
    def draw_trail(self, screen, pos):
        pass


class Hex(Vector3):
    def __init__(self, pos, size, colour: Color, parent_pos=None) -> None:
        super().__init__(pos)
        self.colour = colour
        self.parent_pos = parent_pos
        self.size = size

    def copy_cell(self):
        return Hex((self.x, self.y, self.z), self.size, self.colour)

    @staticmethod
    def make_cell(i, j, size, colour):
        r = j - i//2
        s = 0 - r - i
        return Hex((i, r, s), size, colour)

    @staticmethod
    def draw(screen, cell, coords):
        p2 = []
        for p in Hex.get_points(Vector2(cell.size.x, 0)):
            p2.append(p + coords)
        gfxdraw.filled_polygon(screen, p2, cell.colour)
        draw.polygon(screen, Color("black").lerp(cell.colour, 0.8), p2, 1)

    @staticmethod
    def get_points(unitVector) -> list[Vector2]:
        points = []
        for i in range(6):
            points.append(unitVector.rotate_rad(i*pi/3))
        return points


class HexGrid(Grid):
    def __init__(self, cell_num: Vector2, center: Vector2,
                 colour: Color=Color(0,168,32), size: float=20, pointy=False, overlay=False) -> None:
        super().__init__(cell_num, center, Hex, colour, Vector2(size/2, (size/2)*cos(pi/6)), overlay)
        self.pointy = pointy
        self.unitVector = Vector2(self.size.x, 0).rotate(pointy*30)
        self.generate_cells()

    def get_start_pos(self):
        return self.center - Vector2(self.cell_num.x * self.size.x * 3/4, self.cell_num.y*self.size.y)

    def get_neighbours(self, pos) -> list[Vector3]:
        neighbours = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    if i != j or j != k:
                        rel_pos = pos + Vector3(i, j, k)
                        if self.is_valid_pos(rel_pos) and self.get_cell(rel_pos) is not None:
                            neighbours.append(rel_pos)
        return neighbours

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

    def is_valid_pos(self, pos) -> bool:
        if pos.x + pos.y + pos.z != 0:
            return False
        if pos.x < 0 or  pos.x >= self.cell_num.x:
            return False
        if pos.z > pos.y:
            return False
        if -(pos.x//2) > pos.y or self.cell_num.y-(pos.x//2) <= pos.y:
            return False
        # if pos.x * (pos.y+pos.x//2) >= self.size():
        #     return False
        # if self.get_cell(pos) is None:
        #     return False
        return True

    def pos_to_coords(self, pos: Vector3) -> Vector2:
        # q = x, y = r, z = s
        x = pos.x * self.size.x * 1.5
        y = -pos.x * self.size.y
        y += (pos.x + pos.y) * self.size.y * 2
        if self.pointy:
            return Vector2(y, x) + self.start_pos
        else:
            return Vector2(x, y) + self.start_pos

    def coords_to_pos(self, coords: Vector2) -> Vector3:
        c2 = coords - self.start_pos
        x, y = (c2.y, c2.x) if self.pointy else (c2.x, c2.y)

        x /= self.size.x * 1.5
        x = round(x)
        y += x * self.size.y
        y /= self.size.y * 2
        y = round(y)
        y -= x
        return Vector3(x, y, 0-x-y)

    def draw(self, screen) -> None:
        for cell_row in self.cells:
            for cell in cell_row:
                if cell is not None:
                    coords = self.pos_to_coords(cell)
                    self.cell.draw(screen, cell, coords)
        if self.overlay:
            for cell_row in self.cells:
                for cell in cell_row:
                    if cell is not None and cell.parent_pos is not None:
                        start_pos = self.pos_to_coords(cell)
                        end_pos = self.pos_to_coords(cell.parent_pos)
                        draw.line(screen, (255, 255, 255), start_pos, end_pos)
                # gfxdraw.aapolygon(screen, p2, Color("black"))

    def draw_trail(self, screen, pos):
        p2 = []
        for p in self.cell.get_points(self.unitVector):
            p2.append(p + self.pos_to_coords(pos))
        gfxdraw.filled_polygon(screen, p2, Color('orange'))

    def get_cell(self, pos):
        return super().get_cell(Vector2(pos.x, pos.y + pos.x//2))

    def clear_cell(self, pos):
        return super().clear_cell(Vector2(pos.x, pos.y + pos.x//2))

    def new_cell(self, pos):
        cell = self.cell(pos, self.size, self.colour)
        index = Vector2(pos.x, pos.y + pos.x//2)
        self.cells[int(index.x)][int(index.y)] = cell

    def rotate(self, screen):
        self.pointy = not self.pointy
        self.unitVector = Vector2( self.size.x, 0).rotate(self.pointy*30)
        # self.start_pos = Vector2(-self.cell_num.x * self.size.y, -self.cell_num.y * self.size.x*2/3)+self.center
        self.generate_cells()

        self.draw(screen)

    def move(self, direction, pos):
        if not self.is_valid_pos(pos + direction):
            return pos
        return pos + direction

    def draw_axes(self, screen, font):
        for i in range(int(self.cell_num.x)):
            text = font.render(f"{i}", 1, (255, 0, 0))
            pos = self.start_pos.copy()
            pos.x += i * self.size.x * 1.5 - text.get_width()/2 + 1
            pos.y -= self.size.x * (2 - i % 2)
            screen.blit(text, pos)

        for i in range(int(self.cell_num.y)):
            text = font.render(f"{i:>2}", 1, (255, 0, 0))
            pos = self.start_pos.copy()
            pos.x -= self.size.x * 2 + text.get_width()/2 + 1
            pos.y += self.size.y * 2 * i - text.get_height()/2 + 1
            screen.blit(text, pos)

def main() -> None:
    from pygame import time, event, QUIT
    import pygame as pg
    from player import Player
    # grid = SquareGrid(10, 20, Vector2(50, 50))
    screen = display.set_mode((1280, 720))
    grid = HexGrid(Vector2(10, 10), Vector2(screen.get_size())/2, size=70.0, pointy=False)

    grid.draw(screen)
    clock = time.Clock()
    running = True
    pos = grid.random_pos()
    player = Player(screen, pos, grid.pos_to_coords(pos), Color("red"))
    interval = 200
    lastTime = {pg.K_w:0, pg.K_s:0, pg.K_a:0, pg.K_d:0,
                        pg.K_e:0, pg.K_q:0, pg.K_r:0, pg.K_p:0}
    pg.init()

    myfont = font.Font('freesansbold.ttf', 12)
    while running:
        screen.fill("black")
        for e in event.get():
            if e.type == QUIT:
                running = False

        dt = clock.tick(60) / 1000
        # for i in grid.cells:
        # # render text
        #     text = myfont.render(str(i.pos), 1, (255,255,0))
        #     screen.blit(text, grid.pos_to_coords(i.pos)-grid.size)

        # text = myfont.render(str(grid.coords_to_pos(player.pos)), 1, (255,0,0))
        # screen.blit(text, grid.pos_to_coords(grid.coords_to_pos(player.pos))-grid.size)

        # for v in grid.get_points():
        #     draw.circle(screen, "red", v + player.pos, 5)


        pos = player.pos
        keys = pg.key.get_pressed()
        new_location = player.pos
        if keys[pg.K_w] and pg.time.get_ticks() > interval + lastTime[pg.K_w]:
            lastTime[pg.K_w] = pg.time.get_ticks()
            new_location = grid.move([0, -1, 1], pos)
        if keys[pg.K_s] and pg.time.get_ticks() > interval + lastTime[pg.K_s]:
            lastTime[pg.K_s] = pg.time.get_ticks()
            new_location = grid.move([0, 1, -1], pos)
        if keys[pg.K_d] and pg.time.get_ticks() > interval + lastTime[pg.K_d]:
            lastTime[pg.K_d] = pg.time.get_ticks()
            new_location = grid.move([1, 0, -1], pos)
        if keys[pg.K_q] and pg.time.get_ticks() > interval + lastTime[pg.K_q]:
            lastTime[pg.K_q] = pg.time.get_ticks()
            new_location = grid.move([-1, 0, 1], pos)
        if keys[pg.K_e] and pg.time.get_ticks() > interval + lastTime[pg.K_e]:
            lastTime[pg.K_e] = pg.time.get_ticks()
            new_location = grid.move([1, -1, 0], pos)
        if keys[pg.K_a] and pg.time.get_ticks() > interval + lastTime[pg.K_a]:
            lastTime[pg.K_a] = pg.time.get_ticks()
            new_location = grid.move([-1, 1, 0], pos)
        if keys[pg.K_r] and pg.time.get_ticks() > interval + lastTime[pg.K_r]:
            lastTime[pg.K_r] = pg.time.get_ticks()
            screen.fill("Black")
            grid.rotate(screen)

        if new_location != pos:
            player.move(new_location, grid.pos_to_coords(new_location))
            grid.set_highlight(player.pos)

        grid.draw(screen)
        player.draw(grid.pos_to_coords(pos))
        text = myfont.render(str(grid.coords_to_pos(player.trail[-1])), 1, (0,0,255))
        screen.blit(text, player.trail[-1])
        display.flip()

if __name__ == "__main__":
    main()
