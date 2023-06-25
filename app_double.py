# Example file showing a circle moving on screen
import pygame as pg
from grid import HexGrid
from gameController import GameController
from agents import Node
from queue import PriorityQueue

# pg setup
pg.init()
screen = pg.display.set_mode((1280, 720))
SCREEN_SIZE = pg.Vector2(screen.get_width(), screen.get_height())
CENTER = SCREEN_SIZE / 2
player_pos = CENTER.copy()
TEXT_LEFT_ANCHOR = 20

# create grid
size = 30
# dimensions = pg.Vector2(60, 75)
dimensions = pg.Vector2(21, 22)
grid_pos = CENTER-pg.Vector2(17*15, 0)
grid = HexGrid(dimensions, grid_pos, size=size)
# create walls
goal_pos = grid.random_pos()
wall_num = int(grid.get_size()*0.2)
grid.generate_walls(wall_num, grid.pos_to_coords(goal_pos), grid.pos_to_coords(player_pos))
controller = GameController(screen, grid, goal_pos, "bestFirst",
                            is_random_start=True, change_agent_type=False,
                            wait_time=2500, wall_num=wall_num)

grid_pos = CENTER+pg.Vector2(17*15, 0)
grid2 = HexGrid(dimensions, grid_pos, size=size)
grid2.cells = [cell.copy() if cell is not None else None for cell in grid.cells]
controller2 = GameController(screen, grid2, goal_pos, "astar",
                             is_random_start=True, change_agent_type=False,
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
    dt = clock.tick(40)
    controller.update(screen, dt)
    controller2.update(screen, dt)

    if controller.wait_timer != controller2.wait_timer:
        wait_time = min(controller.wait_timer, controller2.wait_timer)
        controller.wait_timer = wait_time
        controller2.wait_timer = wait_time
    if controller.has_reset or controller2.has_reset:
        c, c2 = controller2, controller
        if controller.has_reset:
            c, c2 = controller, controller
        c.goal.pos = c2.goal.pos.copy()
        # c.reset()
        c.wait_timer = 0
        c.player.pos = c2.player.pos.copy()
        c.agent.open = PriorityQueue()
        c.grid.cells = c2.grid.copy()
        c.has_reset = False
        estimated_cost = c.grid.estimate_remaining_cost(
            c.goal.pos, c.player.pos)
        c.agent.open.put(Node(c.player.pos, None, 0, estimated_cost, 0, c.agent.selected))
        c.player.reset_trail(c.grid.pos_to_coords(c.player.pos))

   # print current trail
    current = controller.agent.current
    trail_counter = 1
    while current is not None and controller.agent.has_goal is not True:
        p2 = []
        for p in controller.grid.get_points():
            p2.append(p + controller.grid.pos_to_coords(current.pos))
        pg.gfxdraw.filled_polygon(screen, p2, pg.Color('orange'))
        current = current.parent
        trail_counter += 1

   # print current trail
    current = controller2.agent.current
    trail_counter = 1
    while current is not None and controller2.agent.has_goal is not True:
        p2 = []
        for p in controller2.grid.get_points():
            p2.append(p + controller2.grid.pos_to_coords(current.pos))
        pg.gfxdraw.filled_polygon(screen, p2, pg.Color('orange'))
        current = current.parent
        trail_counter += 1

    for i, node in enumerate(controller.agent.open.queue):
        text = myfont.render(f"{node.total_cost:.0f}", 1, (255, 255, 255))
        screen.blit(text,
                    controller.grid.pos_to_coords(node.pos)
                    - pg.Vector2(text.get_width()//2-1,text.get_height()//2-2))

    for i, node in enumerate(controller2.agent.open.queue):
        text = myfont.render(f"{node.total_cost:.0f}", 1, (255, 255, 255))
        screen.blit(text,
                    controller2.grid.pos_to_coords(node.pos)
                    - pg.Vector2(text.get_width()//2-1,text.get_height()//2-2))

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