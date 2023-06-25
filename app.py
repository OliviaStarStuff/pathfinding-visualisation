# Example file showing a circle moving on screen
import pygame as pg
from grid import HexGrid
from gameController import GameController

# pg setup
pg.init()
screen = pg.display.set_mode((1600, 768))
SCREEN_SIZE = pg.Vector2(screen.get_width(), screen.get_height())
CENTER = SCREEN_SIZE / 2
player_pos = CENTER.copy()
TEXT_LEFT_ANCHOR = 20


# create grid
grid = HexGrid(pg.Vector2(40, 25), CENTER+pg.Vector2(180, 0), size=30)
goal_pos = grid.random_pos()
wall_num = int(grid.get_size()*0.2)
grid.generate_walls(wall_num, goal_pos, player_pos)
controller = GameController(screen, grid, goal_pos, is_random_start=False, is_regenerate=False,
                            wall_num=wall_num)

myfont = pg.font.SysFont('Consolas', 16)

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
    controller.update(screen, dt)

     # print current trail
    current = controller.agent.current
    trail_counter = 1
    # if current is not None and current.parent is not None:
        # current = current.parent
    while current is not None and controller.agent.has_goal is not True:
        p2 = []
        for p in controller.grid.get_points():
            p2.append(p + controller.grid.pos_to_coords(current.pos))
        pg.gfxdraw.filled_polygon(screen, p2, pg.Color('orange'))
        current = current.parent
        trail_counter += 1

    # Iteration counter
    text = myfont.render(f"iterations: {controller.agent.iteration}", 1, (255, 0, 0))
    screen.blit(text, pg.Vector2(TEXT_LEFT_ANCHOR, 40))

    # Iteration counter
    efficiency = trail_counter/len(controller.agent.closed) if len(controller.agent.closed) > 0 else 0
    if len(controller.agent.path) > 0:
        efficiency = len(controller.agent.path)/len(controller.agent.closed)
    text = myfont.render(f"Efficiency: {efficiency:.3%}", 1, (255, 0, 0))
    screen.blit(text, pg.Vector2(TEXT_LEFT_ANCHOR+160, 40))

    # goal position
    text = myfont.render(f"Goal: {controller.goal.pos}", 1, (255, 0, 0))
    screen.blit(text, pg.Vector2(TEXT_LEFT_ANCHOR, 20))

    # Draw Current Node
    if controller.agent.open.qsize() > 0:
        text = myfont.render(str(f"Current Node: {controller.agent.open.queue[0].pos}"), 1, (255,0,0))
    else:
        text = myfont.render(str(f"Current List: None"), 1, (255,0,0))

    screen.blit(text, pg.Vector2(TEXT_LEFT_ANCHOR, 60))


    # Draw Open List
    text = myfont.render("Open List,     Priority, Total Cost", 1, (255,0,0))
    screen.blit(text, pg.Vector2(TEXT_LEFT_ANCHOR, 80))
    for i, node in enumerate(controller.agent.open.queue):
        text = myfont.render(
            f"{str(node.pos):<14} {node.priority:>8} {node.total_cost:>11}",
            1, (255, 0, 0))
        screen.blit(text, pg.Vector2(TEXT_LEFT_ANCHOR, 100+i*20))
        text = myfont.render(f"{node.estimated_cost:.0f}", 1, (255, 255, 255))
        screen.blit(text,
                    controller.grid.pos_to_coords(node.pos)
                    - pg.Vector2(text.get_width()//2-1,text.get_height()//2-2))

    # draw axes
    for i in range(int(controller.grid.cell_num.x)):
        text = myfont.render(f"{i}", 1, (255, 0, 0))
        pos = controller.grid.start_pos.copy()
        pos.x += i * controller.grid.size.x * 1.5 - text.get_width()/2 + 1
        pos.y -= controller.grid.size.x * (2 - i % 2)
        screen.blit(text, pos)

    for i in range(int(controller.grid.cell_num.y)):
        text = myfont.render(f"{i:>2}", 1, (255, 0, 0))
        pos = controller.grid.start_pos.copy()
        pos.x -= controller.grid.size.x * 2 + 8
        pos.y += controller.grid.size.y * 2 * i - text.get_height()/2 + 1
        screen.blit(text, pos)
    message = "Created by Olivia, CompSci BSC 2022/2023 University of Sheffield"
    text = myfont.render(message, 1, (255, 0, 0))
    screen.blit(text, CENTER + pg.Vector2(-text.get_width()//2, CENTER.y-26))

    # Write algorithm title.
    text = myfont.render(controller.agent.selected.upper(), 1, (255, 0, 0))
    screen.blit(text,  pg.Vector2(TEXT_LEFT_ANCHOR+200, 20))

    pg.display.flip()

pg.quit()