# Example file showing a circle moving on screen
import pygame as pg
from sq_grid import SquareGrid
from gameController import GameController

# pg setup
pg.init()
screen = pg.display.set_mode((1280, 720))
SCREEN_SIZE = pg.Vector2(screen.get_width(), screen.get_height())
CENTER = SCREEN_SIZE / 2
player_pos = CENTER.copy()
TEXT_LEFT_ANCHOR = 20

# create grid
size = pg.Vector2(30,30)
grid_pos = CENTER-pg.Vector2(17*15, 0)
grid = SquareGrid(pg.Vector2(15, 20), grid_pos, size=size)
# create walls
goal_pos = grid.random_pos()
wall_num = int(grid.get_size()*0.07)
grid.generate_walls(wall_num, grid.coords_to_pos(goal_pos), grid.coords_to_pos(player_pos))
controller = GameController(screen, grid, goal_pos, "bestFirst",
                            is_random_start=False, change_agent_type=False,
                            wait_time=2500, wall_num=wall_num)

grid_pos = CENTER+pg.Vector2(17*15, 0)
grid2 = SquareGrid(pg.Vector2(15, 20), grid_pos, size=size)
grid2.cells = grid.copy()
controller2 = GameController(screen, grid2, goal_pos, "astar",
                             is_random_start=False, change_agent_type=False,
                             wait_time=2500, wall_num=wall_num)

myfont = pg.font.SysFont('Consolas', 16)

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
    controller.update(screen, dt)
    controller2.update(screen, dt)

    controller.sync_with(controller2)



   # print current trail
    current = controller.agent.current
    trail_counter = 1
    while current is not None and controller.agent.has_goal is not True:
        coords = controller.grid.pos_to_coords(current.pos)
        coords -= controller.grid.size/2
        dimensions = pg.Rect(coords.x, coords.y, controller.grid.size.x, controller.grid.size.y)
        pg.draw.rect(screen, pg.Color('orange'), dimensions)
        current = current.parent
        trail_counter += 1



   # print current trail
    current = controller2.agent.current
    trail_counter = 1
    while current is not None and controller2.agent.has_goal is not True:
        coords = controller2.grid.pos_to_coords(current.pos)
        coords -= controller2.grid.size/2
        dimensions = pg.Rect(coords.x, coords.y, controller2.grid.size.x, controller2.grid.size.y)
        pg.draw.rect(screen, pg.Color('orange'), dimensions)
        current = current.parent
        trail_counter += 1

    for i, node in enumerate(controller.agent.open.queue):
        text = myfont.render(f"{node.global_cost/30/30:.0f}", 1, (255, 255, 255))
        screen.blit(text,
                    controller.grid.pos_to_coords(node.pos)
                    - pg.Vector2(text.get_width()//2-1,text.get_height()//2-2))

    for i, node in enumerate(controller2.agent.open.queue):
        text = myfont.render(f"{node.global_cost/30/30:.0f}", 1, (255, 255, 255))
        screen.blit(text,
                    controller2.grid.pos_to_coords(node.pos)
                    - pg.Vector2(text.get_width()//2-1,text.get_height()//2-2))


    # draw axes

    # Credits
    message = "Created by Olivia, CompSci BSC 2022/2023 University of Sheffield"
    text = myfont.render(message, 1, (255, 0, 0))
    screen.blit(text, CENTER + pg.Vector2(-text.get_width()//2, CENTER.y-26))

    # Write algorithm title.
    text = myfont.render(controller.agent.selected.upper(), 1, (255, 0, 0))
    screen.blit(text,  pg.Vector2(controller.grid.center.x-text.get_width(), 20))

    # Write algorithm title.
    text = myfont.render(controller2.agent.selected.upper(), 1, (255, 0, 0))
    screen.blit(text,  pg.Vector2(controller2.grid.center.x-text.get_width(), 20))

    pg.display.flip()
    # dt = clock.tick(40)

pg.quit()