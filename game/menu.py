# game/menu.py
import os
import pygame
from game.settings import WHITE, BLACK
from game.button import Button

class Menu:
    def __init__(self, screen, switch_to_new_game, switch_to_load_game, switch_to_pokedex_load):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        self.background = pygame.image.load(os.path.join("assets", "images", "menu_background.jpg"))
        try:
            pygame.mixer.music.load(os.path.join("assets", "sounds", "Main_menu.mp3"))
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Impossible de charger Main_menu.mp3", e)
        self.buttons = [
            Button(200, 50, 400, 50, "New Game", self.font, WHITE, (200, 200, 200), switch_to_new_game),
            Button(200, 150, 400, 50, "Start", self.font, WHITE, (200, 200, 200), switch_to_load_game),
            Button(200, 250, 400, 50, "Pokedex", self.font, WHITE, (200, 200, 200), switch_to_pokedex_load),
            Button(200, 350, 400, 50, "Quit", self.font, WHITE, (200, 200, 200),
                   lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        ]

    def draw(self):
        bg = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(bg, (0, 0))
        for btn in self.buttons:
            btn.draw(self.screen)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
