# Example file showing a circle moving on screen
import pygame as pg
from sq_grid import SquareGrid
from gameController import GameController
from mainController import mainController

# pg setup
pg.init()
screen = pg.display.set_mode((1280, 720))
CENTER = pg.Vector2(screen.get_width(), screen.get_height()) / 2


# create grid
grid = SquareGrid(pg.Vector2(30, 20), CENTER+(180,0), size=pg.Vector2(30,30))
goal_pos = grid.random_pos()
wall_num = int(grid.get_size()*0.1)
controller = GameController(screen, grid, goal_pos, is_random_start=False,
                            wall_num=wall_num, is_regenerate=False)

font = pg.font.SysFont('Consolas', 16)
main_controller = mainController(screen, font, [controller])

clock = pg.time.Clock()
running = True
dt = 0
while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    screen.fill((0,0,16))
    dt = clock.tick(40)
    screen.fill((0,0,16))
    dt = clock.tick(40)
    main_controller.update(dt)

    pg.display.flip()

pg.quit()