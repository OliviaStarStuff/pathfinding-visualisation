# Example file showing a circle moving on screen
import pygame as pg
from grid import HexGrid
from gameController import GameController
from mainController import mainController

# pg setup
pg.init()
screen = pg.display.set_mode((1600, 768))
CENTER = pg.Vector2(screen.get_width(), screen.get_height()) / 2

# create grid
grid = HexGrid(pg.Vector2(40, 25), CENTER+pg.Vector2(180, 0), size=30)

# create grid controller
goal_pos = grid.random_pos()
wall_num = int(grid.get_size()*0.2)
controller = GameController(screen, grid, goal_pos, is_random_start=False,
                            is_regenerate=False, wall_num=wall_num)

# create main controller
font = pg.font.SysFont('Consolas', 16)
main_controller = mainController(screen, font, [controller])

clock = pg.time.Clock()
running = True
dt = 0
pg.mouse.set_cursor(pg.SYSTEM_CURSOR_CROSSHAIR )
while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((0,0,16))
    dt = clock.tick(40)
    main_controller.update(dt)

    pg.display.flip()

pg.quit()