import pygame as pg
from player import Player
from agents import AStar, Goal
from queue import PriorityQueue
from agents import Node


class GameController:
    def __init__(self, screen, grid, goal_pos, agent_type="bfs",
                 key_interval: int=200, wall_num=0, is_regenerate=True,
                 is_random_start=True, change_agent_type=True, wait_time=1000) -> None:
        self.interval = key_interval
        self.lastTime = {pg.K_s:0, pg.K_a:0, pg.K_d:0, pg.K_e:0,
                         pg.K_b:0, pg.K_r:0, pg.K_t:0, pg.K_f:0, pg.K_g: 0,
                         pg.K_v: 0, pg.MOUSEBUTTONDOWN: 0, pg.K_c:0, pg.K_x:0}
        self.grid = grid
        grid.generate_walls(wall_num, goal_pos)

        # create game objects
        self.goal = Goal(screen, goal_pos, pg.Color("blue"))
        self.player = Player(screen, grid.coords_to_pos(grid.start_pos), grid.start_pos, pg.Color("red"))
        self.agent = AStar(self.player, self.goal, grid, agent_type)

        # self.agent = agent
        self.is_started = False
        self.wall_num=wall_num
        self.is_regenerate = is_regenerate
        self.is_random_start = is_random_start
        self.choices = ["bfs", "dfs", "bestFirst", "astar"]
        self.choice = self.choices.index(agent_type)
        self.wait_timer = 0
        self.wait_time = wait_time
        self.change_agent_type = change_agent_type
        self.has_reset = False
        self.step_by_step = False

    def reset(self) -> None:
        self.grid.reset()
        self.agent.randomise_start_and_end(self.is_random_start)
        self.agent.reset()
        self.lastTime[pg.K_r] = pg.time.get_ticks()
        self.has_reset = True
        self.wait_timer = 0

    def regenerate_map(self, wall_num=None):
        wall_num = self.wall_num if wall_num == None else wall_num
        self.grid.generate_cells()
        self.reset()
        self.grid.generate_walls(wall_num, self.agent.goal.pos, self.player.pos)

    def update(self, screen, dt):

        self.grid.draw(screen) # Draw the game grid

        # Key input
        self.check_keys()

        # Only run simulation if it is_started
        if self.is_started and self.agent.update():
            if self.step_by_step:
                self.is_started = False

        # draw objects
        self.player.draw_trail(screen)
        self.agent.draw()
        if not self.agent.active and self.is_started:
            self.wait_timer += dt
            if self.wait_timer > self.wait_time:
                if self.change_agent_type:
                    self.choice += 1
                    self.choice %= len(self.choices)
                    self.agent.selected = self.choices[self.choice]
                if self.is_regenerate:
                    temp, self.is_random_start = self.is_random_start, True
                    self.regenerate_map()
                    self.is_random_start = temp
                else:
                    self.reset()

    def check_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_c] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_c]:
            self.lastTime[pg.K_c] = pg.time.get_ticks()
            self.grid.overlay = not self.grid.overlay

        if keys[pg.K_r] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_r]:
            temp, self.is_random_start = self.is_random_start, True
            self.reset()
            self.is_random_start = temp

        if keys[pg.K_b] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_b]:
            self.lastTime[pg.K_b] = pg.time.get_ticks()
            self.is_random_start = not self.is_random_start

        if keys[pg.K_x] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_x]:
            self.lastTime[pg.K_x] = pg.time.get_ticks()
            self.step_by_step = not self.step_by_step

        if keys[pg.K_s] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_s]:
            self.lastTime[pg.K_s] = pg.time.get_ticks()
            self.is_started = not self.is_started

        if keys[pg.K_t] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_t]:
            self.lastTime[pg.K_t] = pg.time.get_ticks()
            self.change_agent_type = not self.change_agent_type

        if keys[pg.K_e] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_e]:
            self.lastTime[pg.K_e] = pg.time.get_ticks()
            self.choice += 1
            self.choice %= len(self.choices)
            self.agent.selected = self.choices[self.choice]
            self.reset()

        if keys[pg.K_a] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_a]:
            self.lastTime[pg.K_a] = pg.time.get_ticks()
            self.wall_num = int(pg.math.clamp(self.wall_num-50, 0, self.grid.get_size() * 8 / 10))
            self.regenerate_map()

        if keys[pg.K_d] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_d]:
            self.lastTime[pg.K_d] = pg.time.get_ticks()
            self.wall_num = int(pg.math.clamp(self.wall_num+50,0, (self.grid.get_size() * 8) / 10))
            self.regenerate_map()

        if keys[pg.K_f] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_f]:
            self.lastTime[pg.K_f] = pg.time.get_ticks()
            self.is_regenerate = not self.is_regenerate

        if keys[pg.K_g] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_g]:
            self.lastTime[pg.K_g] = pg.time.get_ticks()
            temp, self.is_random_start = self.is_random_start, False
            self.reset()
            self.is_random_start = temp

        if keys[pg.K_v] and pg.time.get_ticks() > self.interval + self.lastTime[pg.K_v]:
            self.lastTime[pg.K_v] = pg.time.get_ticks()
            temp, self.is_random_start = self.is_random_start, True
            self.regenerate_map()
            self.is_random_start = temp

        if pg.time.get_ticks() > self.interval/2 + self.lastTime[pg.MOUSEBUTTONDOWN]:
            self.lastTime[pg.MOUSEBUTTONDOWN] = pg.time.get_ticks()
            vector = pg.Vector2(pg.mouse.get_pos())
            mouse_pos = self.grid.coords_to_pos(vector)
            if pg.mouse.get_pressed()[0] and self.grid.is_valid_pos(mouse_pos):
                if self.grid.get_cell(mouse_pos) is not None:
                    self.grid.clear_cell(mouse_pos)
                else:
                    self.grid.new_cell(mouse_pos)
            elif pg.mouse.get_pressed()[1]:
                self.player.pos = mouse_pos
                self.agent.reset_open()
            elif pg.mouse.get_pressed()[2]:
                self.goal.pos = mouse_pos
                self.agent.reset_open()

    def sync_with(self, other):
        if self.wait_timer != other.wait_timer:
            wait_time = min(self.wait_timer, other.wait_timer)
            self.wait_timer = wait_time
            other.wait_timer = wait_time
        if self.has_reset or other.has_reset:
            c, c2 = other, self
            if self.has_reset:
                c, c2 = self, other
            c.goal.pos = c2.goal.pos.copy()
            # c.reset()
            c.player.pos = c2.player.pos.copy()
            c.agent.open = PriorityQueue()
            c.grid.cells = c2.grid.copy()
            c.has_reset = False
            c2.has_reset = False
            estimated_cost = c.grid.estimate_remaining_cost(
                c.goal.pos, c.player.pos)
            c.agent.open.put(Node(c.player.pos, None, 0, estimated_cost, 0, c.agent.selected))
            c.player.reset_trail(c.grid.pos_to_coords(c.player.pos))