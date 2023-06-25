from pygame import Vector2, Color, draw, surface, Rect
from random import randint

class Cell(Vector2):
    def __init__(self, x: float, y: float, colour: Color=Color(0,168,32), parent_pos = None) -> None:
        super().__init__(x, y)
        self.colour = colour
        self.parent_pos = parent_pos
    def copy(self):
        return Cell(self.x, self.y, self.colour)

class SquareGrid:
    def __init__(self, cell_num:Vector2, center: Vector2,
                 colour: Color=Color(0,168,32), size: Vector2= Vector2(40, 40), overlay=False) -> None:
        self.overlay = overlay
        self.size = size
        self.cell_num = cell_num
        self.colour = colour
        self.center = center
        self.start_pos = center - size.elementwise() * cell_num/2
        self.generate_cells()

    def generate_cells(self):
        self.cells = []
        for i in range(int(self.cell_num.x)):
            col = []
            for j in range(int(self.cell_num.y)):
                col.append(Cell(i, j, self.colour))
            self.cells.append(col)

    def generate_walls(self, number_of_walls, goal_pos, player_pos=Vector2(0,0)):
        for i in range(number_of_walls):
            random_pos = self.random_pos()
            while not self.is_valid_pos(random_pos) or random_pos == goal_pos or random_pos == player_pos:
                random_pos = self.random_pos()
            if self.cells[int(random_pos.x)][int(random_pos.y)] != self.coords_to_pos(self.start_pos) \
            and self.cells[int(random_pos.x)][int(random_pos.y)] != goal_pos:
                self.cells[int(random_pos.x)][int(random_pos.y)] = None

    def reset(self):
         for col in self.cells:
            for cell in col:
                if cell is not None:
                    cell.colour = self.colour
                    cell.parent_pos = None

    def draw_trail(self, screen, pos):
        p2 = []
        coords = self.pos_to_coords(pos)
        coords -= self.size/2
        dimensions = Rect(coords.x, coords.y, self.size.x, self.size.y)
        draw.rect(screen, Color('orange'), dimensions)


    def pos_to_coords(self, pos):
        return pos.elementwise() * self.size + self.start_pos

    def coords_to_pos(self, coords):
        return round((coords - self.start_pos).elementwise() / self.size)

    def random_pos(self):
        while True:
            pos = Vector2(randint(0, self.cell_num.x - 1), randint(0, self.cell_num.y - 1))
            if self.is_valid_pos(pos):
                return pos

    def copy(self):
        cells = []

        for cell_row in self.cells:
            new_cell_row = []
            for cell in cell_row:
                if cell is not None:
                    new_cell_row.append(cell.copy())
                else:
                    new_cell_row.append(None)
            cells.append(new_cell_row)
        return cells

    def get_size(self):
        return self.size.x * self.size.y

    def draw(self, screen: surface):
        for col in self.cells:
            for cell in col:
                if cell is not None:
                    coords = self.pos_to_coords(cell)
                    coords -= self.size/2
                    dimensions = Rect(coords.x, coords.y, self.size.x, self.size.y)
                    draw.rect(screen, cell.colour, dimensions)
                    draw.rect(screen, Color("black"), dimensions, 1)
        if self.overlay:
            for col in self.cells:
                for cell in col:
                    if cell is not None and cell.parent_pos is not None and cell.colour != Color(168,0,168):
                        start_pos = self.pos_to_coords(cell)
                        end_pos = self.pos_to_coords(cell.parent_pos)
                        draw.line(screen, (255, 255, 255), start_pos, end_pos)

    def set_parent(self, pos, parent_pos):
        self.cells[int(pos.x)][int(pos.y)].parent_pos = parent_pos

    def is_valid_pos(self, pos) -> bool:

        if pos.x >= self.cell_num.x or pos.x < 0:
            return False
        if pos.y >= self.cell_num.y or pos.y < 0:
            return False
        if self.cells[int(pos.x)][int(pos.y)] is None:
            return False
        return True

    def get_cell(self, pos):
        return self.cells[int(pos.x)][int(pos.y)]

    def clear_cell(self, pos):
        self.cells[int(pos.x)][int(pos.y)] = None

    def new_cell(self, pos):
        cell = Cell(pos, self.colour)
        self.cells[int(pos.x)][int(pos.y)] = cell

    def set_highlight(self, pos, colour: Color=Color(168,0,168)):
        if self.is_valid_pos(pos):
            self.cells[int(pos.x)][int(pos.y)].colour = colour
        else:
            print("not valid", pos)

    def get_neighbours(self, pos):
        neighbours = []
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if abs(i) != abs(j) and (abs(i) == 1 or abs(j) == 1) and self.is_valid_pos(pos + Vector2(i, j)):
                # if ((i == j and i != 0) or i != j) and self.is_valid_pos(pos + Vector2(i, j)):
                    neighbours.append(pos + Vector2(i, j))
        return neighbours

    def estimate_remaining_cost(self, pos_1: Vector2, pos_2: Vector2):
        distance: Vector2 = pos_1 - pos_2
        return abs(distance.x)+abs(distance.y)
        distance.x /= self.size.x
        distance.y /= self.size.y
        return distance.magnitude_squared()

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