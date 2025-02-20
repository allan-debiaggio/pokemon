# game/pokedex_screen.py
import os
import pygame
from game.settings import WHITE, BLACK, WIDTH, HEIGHT
from game.button import Button

class PokedexScreen:
    def __init__(self, screen, pokedex, switch_to_previous):
        self.screen = screen
        self.pokedex = pokedex
        self.switch_to_previous = switch_to_previous
        self.font = pygame.font.Font(None, 30)
        self.selected_pokemon = None
        self.scroll_offset = 0
        self.background = pygame.image.load(os.path.join("assets", "images", "background_pokedex.png"))
        self.back_button = Button(650, 500, 120, 40, "Back", self.font, WHITE, (200, 200, 200), self.switch_to_previous)

    def draw(self):
        bg = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(bg, (0, 0))
        y_offset = 100 - self.scroll_offset
        self.entry_rects = []
        for p in self.pokedex.caught_pokemon:
            rect = pygame.Rect(50, y_offset, self.screen.get_width() - 100, 120)
            color = WHITE if p.current_hp > 0 else (255, 0, 0)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=10)
            if p.sprite:
                scaled_sprite = pygame.transform.scale(p.sprite, (80, 80))
                self.screen.blit(scaled_sprite, (rect.x + 10, rect.y + 20))
            else:
                pygame.draw.rect(self.screen, BLACK, (rect.x + 10, rect.y + 20, 80, 80))
            self.screen.blit(self.font.render("Nom: " + p.name, True, BLACK), (rect.x + 110, rect.y + 10))
            self.screen.blit(self.font.render("HP: " + str(p.current_hp) + " / " + str(p.hp), True, BLACK), (rect.x + 110, rect.y + 40))
            self.screen.blit(self.font.render("Niveau: " + str(p.level), True, BLACK), (rect.x + 110, rect.y + 70))
            self.entry_rects.append((rect, p))
            y_offset += 140
        self.back_button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(0, min(self.scroll_offset - event.y * 20,
                                            (100 + len(self.pokedex.caught_pokemon) * 140) - self.screen.get_height()))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if self.back_button.rect.collidepoint(pos):
                self.back_button.handle_event(event)
                return True
            for rect, p in self.entry_rects:
                if rect.collidepoint(pos):
                    if p.current_hp > 0:
                        self.selected_pokemon = p
                        self.switch_to_previous()
                    else:
                        print(f"{p.name} est K.O. et ne peut pas combattre!")
                    return True
        return False

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.selected_pokemon = None
                if self.handle_event(event):
                    running = False
            self.draw()
            pygame.display.flip()
            clock.tick(30)
        return self.selected_pokemon
