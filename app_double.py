# Example file showing a circle moving on screen
import pygame as pg
from grid import HexGrid
from gameController import GameController
from mainController import mainController

# pg setup
pg.init()
screen = pg.display.set_mode((1280, 720))
CENTER = pg.Vector2(screen.get_width(), screen.get_height()) / 2

# create grid
size = 30
# dimensions = pg.Vector2(60, 75)
dimensions = pg.Vector2(21, 22)
grid_pos = CENTER-pg.Vector2(17*15, 0)
grid = HexGrid(dimensions, grid_pos, size=size)
# create walls
goal_pos = grid.random_pos()
wall_num = int(grid.get_size()*0.2)
controller = GameController(screen, grid, goal_pos, "bfs",
                            is_random_start=True, change_agent_type=False,
                            wait_time=2500, wall_num=wall_num)

grid_pos = CENTER+pg.Vector2(17*15, 0)
grid2 = HexGrid(dimensions, grid_pos, size=size)
grid2.cells = [cell.copy() if cell is not None else None for cell in grid.cells]
controller2 = GameController(screen, grid2, goal_pos, "astar",
                             is_random_start=True, change_agent_type=False,
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
    dt = clock.tick(40)

    main_controller.update(dt)
    controller.sync_with(controller2)

    pg.display.flip()

pg.quit()