# button.py
import os
import pygame
from game.settings import WHITE, BLACK

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        current_color = self.hover_color if is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=10)
        text_surf = self.font.render(self.text, True, BLACK)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))
        if is_hovered:
            triangle_points = [
                (self.rect.left + 10, self.rect.centery - 5),
                (self.rect.left + 10, self.rect.centery + 5),
                (self.rect.left + 20, self.rect.centery)
            ]
            pygame.draw.polygon(screen, BLACK, triangle_points)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                try:
                    sound = pygame.mixer.Sound(os.path.join("assets", "sounds", "Button.mp3"))
                    sound.play()
                except Exception as e:
                    print("Impossible de jouer Button.mp3", e)
                self.action()
