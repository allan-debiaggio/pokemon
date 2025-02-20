# game/load_game_screen.py
import os
import json
import pygame
from game.settings import WHITE, BLACK
from game.button import Button

SLOT_FILES = {
    1: "save_slot_1.json",
    2: "save_slot_2.json",
    3: "save_slot_3.json"
}

class LoadGameScreen:
    def __init__(self, screen, switch_to_main_menu, load_callback, center_slots=False):
        self.screen = screen
        self.font = pygame.font.Font(None, 30)
        self.switch_to_main_menu = switch_to_main_menu
        self.load_callback = load_callback
        self.slot_buttons = []
        slot_x = (self.screen.get_width() - 200) // 2 if center_slots else 100
        for i in range(1, 4):
            btn = Button(slot_x, 100 + (i - 1) * 70, 200, 50,
                         f"Slot {i}", self.font, WHITE, (200, 200, 200),
                         action=lambda i=i: self.select_slot(i))
            self.slot_buttons.append(btn)
        self.selected_slot = None
        self.input_box = pygame.Rect(400, 200, 300, 50)
        self.game_name = ""
        self.back_button = Button(400, 400, 150, 50, "Back", self.font, WHITE, (200, 200, 200), self.switch_to_main_menu)
        self.input_active = False
        self.background = pygame.image.load(os.path.join("assets", "images", "menu_selector.jpg"))

    def select_slot(self, slot):
        self.selected_slot = slot
        slot_file = SLOT_FILES[slot]
        if os.path.exists(slot_file):
            self.load_callback(slot, None)
        else:
            self.input_active = True
            self.game_name = ""

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for btn in self.slot_buttons:
                if btn.rect.collidepoint(pos):
                    btn.handle_event(event)
            self.back_button.handle_event(event)
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN and self.game_name.strip() != "":
                self.load_callback(self.selected_slot, self.game_name.strip())
            elif event.key == pygame.K_BACKSPACE:
                self.game_name = self.game_name[:-1]
            else:
                self.game_name += event.unicode

    def draw(self):
        bg = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(bg, (0, 0))
        self.screen.blit(self.font.render("Select a Game Slot", True, BLACK), (100, 50))
        for i, btn in enumerate(self.slot_buttons, start=1):
            slot_file = SLOT_FILES[i]
            if os.path.exists(slot_file):
                try:
                    with open(slot_file, 'r') as f:
                        data = json.load(f)
                        game_name = data.get("game_name", "Unknown")
                except:
                    game_name = "Unknown"
            else:
                game_name = "Empty"
            btn.text = f"Slot {i}: {game_name}"
            btn.draw(self.screen)
        if self.input_active:
            pygame.draw.rect(self.screen, WHITE, self.input_box)
            pygame.draw.rect(self.screen, BLACK, self.input_box, 2)
            self.screen.blit(self.font.render(self.game_name, True, BLACK),
                             (self.input_box.x + 5, self.input_box.y + 10))
        self.back_button.draw(self.screen)
