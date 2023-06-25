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
size = pg.Vector2(30,30)
grid_pos = CENTER-pg.Vector2(17*15, 0)
grid = SquareGrid(pg.Vector2(15, 20), grid_pos, size=size)
goal_pos = grid.random_pos()

wall_num = int(grid.get_size()*0.07)
controller = GameController(screen, grid, goal_pos, "bestFirst",
                            is_random_start=False, change_agent_type=False,
                            wait_time=2500, wall_num=wall_num)

grid_pos = CENTER+pg.Vector2(17*15, 0)
grid2 = SquareGrid(pg.Vector2(15, 20), grid_pos, size=size)
grid2.cells = grid.copy()

controller2 = GameController(screen, grid2, goal_pos, "astar",
                             is_random_start=False, change_agent_type=False,
                             wait_time=2500, wall_num=wall_num)

controller2.grid.cells = controller.grid.copy()
controller2.agent.reset_open()

font = pg.font.SysFont('Consolas', 16)
main_controller = mainController(screen, font, [controller, controller2], False)

clock = pg.time.Clock()
running = True
dt = 0
while running:
    # poll for events
    # pg.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    # fill the screen with a color to wipe away anything from last frame
    screen.fill((0,0,16))
    dt = clock.tick(60)

    main_controller.update(dt)
    controller.sync_with(controller2)

    pg.display.flip()

pg.quit()