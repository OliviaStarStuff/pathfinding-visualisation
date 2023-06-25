import pygame as pg

class mainController:
    CONTROLS_TEXT = "s:start/stop a:fewer walls d:more walls e:next algorithm \
r:regen positions v:regen map g:restart b:randomise positions"
    CREDITS_TEXT = "Created by Olivia, CompSci BSC 2022/2023 University of Sheffield"
    TOGGLE_TEXT = "f:regen map toggle t:switch algorithms c:show graph overlap \
c:show graph overlap x:run step by step (press s)"
    TEXT_LEFT_ANCHOR = 20

    def __init__(self, screen, font, controllers, is_draw_ui=True):
        self.screen = screen
        self.CENTER = pg.Vector2(screen.get_size()) / 2
        player_pos = self.CENTER.copy()
        self.controllers = controllers
        self.font = font
        self.is_draw_ui = is_draw_ui

    def write_iteration_counter(self, controller):
        text = self.font.render(f"iterations: {controller.agent.iteration}", 1, (255, 0, 0))
        self.screen.blit(text, pg.Vector2(self.TEXT_LEFT_ANCHOR, 40))

    def write_efficiency_value(self, controller):
        efficiency = controller.agent.get_efficiency()
        text = self.font.render(f"Efficiency: {efficiency:.3%}", 1, (255, 0, 0))
        self.screen.blit(text, pg.Vector2(self.TEXT_LEFT_ANCHOR+160, 40))

    def write_goal_position(self, controller):
        text = self.font.render(f"Goal: {controller.goal.pos}", 1, (255, 0, 0))
        self.screen.blit(text, pg.Vector2(self.TEXT_LEFT_ANCHOR, 20))

    def write_current_node(self, controller):
        if controller.agent.open.qsize() > 0:
            text = self.font.render(str(f"Current Node: {controller.agent.open.queue[0].pos}"), 1, (255,0,0))
        else:
            text = self.font.render(str(f"Current List: None"), 1, (255,0,0))
        self.screen.blit(text, pg.Vector2(self.TEXT_LEFT_ANCHOR, 60))

    def write_open_list(self, controller):
        text = self.font.render("Open List,     Priority, Total Cost", 1, (255,0,0))
        self.screen.blit(text, pg.Vector2(self.TEXT_LEFT_ANCHOR, 80))
        for i, node in enumerate(controller.agent.open.queue):
            text = self.font.render(
                f"{str(node.pos):<14} {node.priority:>8} {node.total_cost:>11}",
                1, (255, 0, 0))
            self.screen.blit(text, pg.Vector2(self.TEXT_LEFT_ANCHOR, 100+i*20))

    def write_algorithm_title(self, controller):
        text = self.font.render(controller.agent.selected.upper(), 1, (255, 0, 0))
        self.screen.blit(text,  pg.Vector2(self.TEXT_LEFT_ANCHOR+200, 20))

    def draw_statistics(self, controller):
        self.write_iteration_counter(controller)
        self.write_efficiency_value(controller)
        self.write_goal_position(controller)
        self.write_current_node(controller)
        self.write_algorithm_title(controller)
        self.write_open_list(controller)

    def draw_axes(self, controller):
        for i in range(int(controller.grid.cell_num.x)):
            text = self.font.render(f"{i}", 1, (255, 0, 0))
            pos = controller.grid.start_pos.copy()
            pos.x += i * controller.grid.size.x * 1.5 - text.get_width()/2 + 1
            pos.y -= controller.grid.size.x * (2 - i % 2)
            self.screen.blit(text, pos)

        for i in range(int(controller.grid.cell_num.y)):
            text = self.font.render(f"{i:>2}", 1, (255, 0, 0))
            pos = controller.grid.start_pos.copy()
            pos.x -= controller.grid.size.x * 2 + 8
            pos.y += controller.grid.size.y * 2 * i - text.get_height()/2 + 1
            self.screen.blit(text, pos)

    def write_controls(self):
        message = self.CONTROLS_TEXT
        text = self.font.render(message, 1, (255, 0, 0))
        self.screen.blit(text,
                        self.CENTER
                        + pg.Vector2(-text.get_width()/2, self.CENTER.y-42))

        message = self.TOGGLE_TEXT
        text = self.font.render(message, 1, (255, 0, 0))
        self.screen.blit(text,
                    self.CENTER + pg.Vector2(-text.get_width()/2, self.CENTER.y-58))

    def write_credits(self):
        message = self.CREDITS_TEXT
        text = self.font.render(message, 1, (255, 0, 0))
        self.screen.blit(text,
                        self.CENTER
                        + pg.Vector2(-text.get_width()/2, self.CENTER.y-26))

    def write_cell_values(self, controller):
        for node in controller.agent.open.queue:
            text = self.font.render(
                f"{node.global_cost:.0f}", 1, (255, 255, 255))
            coords = controller.grid.pos_to_coords(node.pos)
            coords -= pg.Vector2(text.get_width()//2-1,text.get_height()//2-2)

            self.screen.blit(text, coords)

    def draw_UI(self, controller):
        self.draw_statistics(controller)
        self.write_open_list(controller)
        self.draw_axes(controller)

    def update(self, dt):

        for controller in self.controllers:
            controller.update(self.screen, dt)
            self.write_cell_values(controller)
            if self.is_draw_ui:
                self.draw_UI(controller)
            controller.agent.draw_current_trail(self.screen)

        self.write_controls()
        self.write_credits()

        pg.display.flip()