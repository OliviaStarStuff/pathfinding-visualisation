from pygame import Vector2, Color, draw, surface, Rect
from grid import Grid

class Cell(Vector2):
    def __init__(self, pos: float, size: Vector2, colour: Color=Color(0,168,32), parent_pos = None) -> None:
        super().__init__(pos)
        self.colour = colour
        self.parent_pos = parent_pos
        self.size = size
    def __copy__(self):
        return Cell((self.x, self.y), self.size, self.colour)

    @staticmethod
    def make_cell(i, j, size, colour):
        return Cell((i, j), size, colour)

    @staticmethod
    def draw(screen, cell, coords):
        corner = coords - cell.size/2
        dimensions = Rect(corner.x, corner.y, cell.size.x, cell.size.y)
        draw.rect(screen, cell.colour, dimensions)
        draw.rect(screen, Color("black"), dimensions, 1)

class SquareGrid(Grid):
    def __init__(self, cell_num:Vector2, center: Vector2,
                 colour: Color=Color(0,168,32), size: Vector2= Vector2(40, 40), overlay=False) -> None:
        super().__init__(cell_num, center, Cell, colour, size, overlay)

    def get_neighbours(self, pos):
        neighbours = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if abs(i) != abs(j) and (abs(i) == 1 or abs(j) == 1):
                    rel_pos = pos + Vector2(i, j)
                    if self.is_valid_pos(rel_pos) and self.cells[int(rel_pos.x)][int(rel_pos.y)] is not None:
                        # if ((i == j and i != 0) or i != j) and self.is_valid_pos(pos + Vector2(i, j)):
                        neighbours.append(pos + Vector2(i, j))
        return neighbours

    def estimate_remaining_cost(self, pos_1: Vector2, pos_2: Vector2):
        distance: Vector2 = (pos_1 - pos_2)
        return abs(distance.x)+abs(distance.y)
        distance.x /= self.size.x
        distance.y /= self.size.y
        return distance.magnitude_squared()

    def is_valid_pos(self, pos) -> bool:
        if pos.x >= self.cell_num.x or pos.x < 0:
            return False
        if pos.y >= self.cell_num.y or pos.y < 0:
            return False
        return True

    def pos_to_coords(self, pos: Vector2) -> Vector2:
        return pos.elementwise() * self.size + self.start_pos

    def coords_to_pos(self, coords: Vector2) -> Vector2:
        return round((coords - self.start_pos).elementwise() / self.size)

    def draw(self, screen: surface):
        for col in self.cells:
            for cell in col:
                if cell is not None:
                    coords = self.pos_to_coords(cell)
                    self.cell.draw(screen, cell, coords)
        if self.overlay:
            for col in self.cells:
                for cell in col:
                    if cell is not None and cell.parent_pos is not None and cell.colour != Color(168,0,168):
                        start_pos = self.pos_to_coords(cell)
                        end_pos = self.pos_to_coords(cell.parent_pos)
                        draw.line(screen, (255, 255, 255), start_pos, end_pos)

    def draw_trail(self, screen, pos):
        coords = self.pos_to_coords(pos)
        coords -= self.size/2
        dimensions = Rect(coords.x, coords.y, self.size.x, self.size.y)
        draw.rect(screen, Color('orange'), dimensions)


def main():
    from pygame import time, event, QUIT, display, font
    import pygame as pg
    from player import Player

    pg.init()

    screen = display.set_mode((1280, 720))
    CENTER = Vector2(display.get_window_size())/2
    grid = SquareGrid(Vector2(10, 10), CENTER, size=Vector2(40,40))
    player_pos = grid.random_pos()
    player = Player(screen, player_pos, grid.pos_to_coords(player_pos), Color('red'))

    clock = time.Clock()
    running = True
    interval = 200
    lastTime = {pg.K_w:0, pg.K_s:0, pg.K_a:0, pg.K_d:0,
                        pg.K_e:0, pg.K_q:0, pg.K_r:0, pg.K_p:0}

    while running:
        screen.fill("black")
        for e in event.get():
            if e.type == QUIT:
                running = False

        grid.draw(screen)
        player.draw(grid.pos_to_coords(player.pos))
        myfont = font.Font('freesansbold.ttf', 12)
        display.flip()

if __name__ == "__main__":
    main()