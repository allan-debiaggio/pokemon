# game/submenu.py
import os
import pygame
from game.settings import WHITE, BLACK
from game.button import Button

class SubMenu:
    def __init__(self, screen, switch_to_main_menu):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        self.background = pygame.image.load(os.path.join("assets", "images", "menu_selector.jpg"))
        self.buttons = [
            Button(200, 200, 400, 50, "Resume", self.font, WHITE, (200, 200, 200),
                   lambda: print("Resuming game...")),
            Button(200, 300, 400, 50, "Main Menu", self.font, WHITE, (200, 200, 200), switch_to_main_menu)
        ]

    def draw(self):
        bg = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(bg, (0, 0))
        for btn in self.buttons:
            btn.draw(self.screen)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
