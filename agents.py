from __future__ import annotations
from player import Player, Goal
from grid import HexGrid
from random import choice
from pygame import Vector2, Vector3, time, Color, math
from abc import ABC, abstractmethod
from collections import deque
from queue import PriorityQueue

class Agent(ABC):
    def __init__(self, player: Player, goal: Goal, grid: HexGrid,
                 selected: str) -> None:
        super().__init__()
        self.player = player
        self.goal = goal
        self.grid = grid
        self.selected = selected
        self.trail = 0

        self.reset()

    def reset(self) -> None:
        self.player.reset_trail(self.grid.pos_to_coords(self.player.pos))


        self.closed: deque[Node] = deque()
        self.current: Node = None
        self.path: deque[Node] = deque()

        self.has_goal = False
        self.path_index = 0
        self.iteration = 0
        self.priority_index = 1
        self.active = True

        self.reset_open()

    def reset_open(self):
        self.open: PriorityQueue[Node] = PriorityQueue()
        estimated_cost = self.grid.estimate_remaining_cost(
            self.goal.pos, self.player.pos)
        self.open.put(Node(self.player.pos, None, 0, estimated_cost, 0, self.selected))

    def randomise_start_and_end(self, is_random) -> None:
        if is_random:
            self.goal.pos = self.grid.random_pos()
            self.player.pos = self.grid.random_pos()
        else:
            self.player.pos = self.grid.coords_to_pos(self.player.trail[0])

    def get_efficiency(self):
        efficiency = 0
        if len(self.closed) > 0:
            efficiency = self.trail_counter/len(self.closed)
        if len(self.path) > 0:
            efficiency = len(self.path)/len(self.closed)
        return efficiency

    def draw_current_trail(self, screen):
        current = self.current
        self.trail_counter = 1
        while current is not None and self.has_goal is not True:
            self.grid.draw_trail(screen, current.pos)
            current = current.parent
            self.trail_counter += 1

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def get_neighbours(self):
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def estimate_remaining_cost(self) -> None:
        return 0


class RandomAgent(Agent):
    def __init__(self, player: Player, goal: Goal, grid: HexGrid) -> None:
        super().__init__(player, goal, grid)

    def update(self) -> None:
        if not self.has_goal and self.is_ready():
            self.time = time.get_ticks()
            self.player.move(self.choose_moves())
            self.has_goal = self.found_goal()

    def choose_moves(self) -> Vector2:
        return self.grid.move(choice(self.moves), choice((-1, 1)), self.player.pos)

    def is_ready(self):
        return time.get_ticks() > self.interval + self.time

class Node:
    def __init__(self, pos: math._GenericVector,  parent: Node,
                 global_cost: float, estimated_cost: float=0,
                 priority: int=0, selected: str="astar") -> None:
        self.pos = pos
        self.parent = parent

        self.global_cost = global_cost
        self.estimated_cost = estimated_cost
        self.total_cost = global_cost + estimated_cost

        self.priority = priority
        self.options = {"dfs": self.dfs, "bfs": self.bfs,
                        "astar": self.astar, "bestFirst": self.bestFirst,
                        "bestFirst2":self.bestFirst2}
        self.selected = selected

    def update_costs(self, parent: Node, global_cost: float, estimated_cost: float):
        self.global_cost = global_cost
        self.total_cost = global_cost + estimated_cost
        self.estimated_cost = estimated_cost
        self.parent = parent

    def __lt__(self, other):
        return self.options[self.selected](other)

    def astar(self, other):
        if self.total_cost == other.total_cost:
            if self.global_cost == other.global_cost:
                return self.priority > other.priority
            return self.global_cost < other.global_cost
        return self.total_cost < other.total_cost

    def bfs(self, other):
        return self.priority < other.priority

    def dfs(self, other):
        return self.priority > other.priority

    def bestFirst(self, other):
        if self.estimated_cost == other.estimated_cost:
            return self.priority > other.priority
            # return self.global_cost > other.global_cost
        return self.estimated_cost < other.estimated_cost

    def bestFirst2(self, other):
        if self.estimated_cost == other.estimated_cost:
            return self.global_cost < other.global_cost
        return self.estimated_cost < other.estimated_cost

class AStar(Agent):
    def __init__(self, player, goal: Goal, grid, selected) -> None:
        super().__init__(player, goal, grid, selected)

    def draw(self):
        self.player.draw(self.grid.pos_to_coords(self.player.pos))
        self.goal.draw(self.grid.pos_to_coords(self.goal.pos))

    def get_neighbours(self):
        adjacents = self.grid.get_neighbours(self.current.pos)

        closed_positions = [c.pos for c in self.closed]
        opened_positions = [o.pos for o in self.open.queue]

        for adjacent in adjacents:
            global_cost = self.current.global_cost + self.grid.estimate_remaining_cost(adjacent, self.current.pos)
            if adjacent not in closed_positions:
                estimated_remaining_cost = self.grid.estimate_remaining_cost(self.goal.pos, adjacent)

                if adjacent in opened_positions:
                    # get node
                    for node in self.open.queue:
                        if node.pos == adjacent and node.global_cost > global_cost:
                            node.update_costs(
                            self.current, global_cost, estimated_remaining_cost)
                else:
                    node = Node(adjacent, self.current, global_cost, estimated_remaining_cost, self.priority_index, self.selected)
                    self.priority_index += 1
                    self.open.put(node)
                    self.grid.set_highlight(adjacent)
                    self.grid.set_parent(adjacent, self.current.pos)

    def estimate_remaining_cost(self, pos_1: Vector2, pos_2: Vector2):
        # d_pos = pos_1 - pos_2
        # distance = 0
        # for i in d_pos[:]:
        #     if i > 0:
        #         distance += i
        # return distance
        distance: Vector2 = self.grid.pos_to_coords(pos_1) - self.grid.pos_to_coords(pos_2)
        return abs(distance.x)+abs(distance.y)
        distance.x /= self.grid.size.x
        distance.y /= self.grid.size.y
        return distance.magnitude_squared()

    def update(self):
        if not self.active:
            return False

        # if we haven't found goal,
        if not self.has_goal:

            # if there are no more open nodes end program
            if self.open.qsize() == 0:
                self.current = None
                self.active = False
                pos = self.grid.get_cell(self.player.pos)
                if pos is not None:
                    pos.colour = Color('blue')
                return False
            self.current = self.open.get()

            self.iteration+=1

            self.get_neighbours()

            # self.grid.set_highlight(self.open.queue[0].pos, Color(240,0,240))
            if self.open.qsize() > 0:
                self.grid.set_highlight(self.current.pos, Color('blue'))

            if self.current.pos == self.goal.pos:
                self.grid.set_highlight(self.current.pos)
                self.has_goal = True
                pos = self.grid.get_cell(self.current.pos)
                # if pos is not None:
                pos.colour = Color('orange')

                current = self.current
                while current.parent is not None:
                    self.path.append(current)
                    current = current.parent

                self.path.reverse()
                pos = self.grid.get_cell(self.current.pos)
                if pos is not None:
                    pos.colour = Color('Green')

            self.closed.append(self.current)
            self.open.task_done()
        # Move Player
        elif self.path_index < len(self.path):
            pos = self.path[self.path_index].pos
            self.player.move(pos, self.grid.pos_to_coords(pos))
            self.path_index += 1
        else:
            self.active = False
            return False
        return True

