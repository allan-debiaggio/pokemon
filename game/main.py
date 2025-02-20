# game/main.py
import os
import pygame
from game.settings import WIDTH, HEIGHT, SLOT_FILES
from game.menu import Menu
from game.submenu import SubMenu
from game.pokedex_screen import PokedexScreen
from game.load_game_screen import LoadGameScreen
from game.game_logic import Game, new_game

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pokemon Battle")
    clock = pygame.time.Clock()
    current_state = "menu"  # "menu", "battle", "pokedex", "submenu", "load_game", "new_game"
    game_instance = None
    load_game_screen = None
    new_game_screen = None
    pokedex_screen = None

    def load_game_callback(slot, game_name):
        nonlocal current_state, game_instance
        filename = SLOT_FILES[slot]
        if os.path.exists(filename) and game_name is None:
            game_instance = Game(save_file=filename)
        else:
            game_instance = new_game(slot, game_name)
        current_state = "battle"

    def load_pokedex_callback(slot, game_name):
        nonlocal current_state, pokedex_screen
        filename = SLOT_FILES[slot]
        if os.path.exists(filename):
            from game.utils import load_game
            pdex = load_game(filename)
        else:
            from game.pokedex import Pokedex
            pdex = Pokedex()
        pokedex_screen = PokedexScreen(screen, pdex, switch_to_main_menu)
        current_state = "pokedex"

    def switch_to_new_game():
        nonlocal current_state, new_game_screen
        current_state = "new_game"
        new_game_screen = LoadGameScreen(screen, switch_to_main_menu, load_game_callback, center_slots=False)

    def switch_to_load_game():
        nonlocal current_state, load_game_screen
        current_state = "load_game"
        load_game_screen = LoadGameScreen(screen, switch_to_main_menu, load_game_callback, center_slots=True)

    def switch_to_pokedex_load():
        nonlocal current_state, load_game_screen
        current_state = "load_game"
        load_game_screen = LoadGameScreen(screen, switch_to_main_menu, load_pokedex_callback, center_slots=True)

    def switch_to_main_menu():
        nonlocal current_state
        current_state = "menu"

    menu_screen = Menu(screen, switch_to_new_game, switch_to_load_game, switch_to_pokedex_load)
    submenu_screen = SubMenu(screen, switch_to_main_menu)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if current_state == "menu":
                menu_screen.handle_event(event)
            elif current_state == "submenu":
                submenu_screen.handle_event(event)
            elif current_state == "pokedex":
                if pokedex_screen:
                    pokedex_screen.handle_event(event)
            elif current_state == "battle" and game_instance:
                game_instance.handle_event(event)
            elif current_state == "load_game":
                if load_game_screen:
                    load_game_screen.handle_event(event)
            elif current_state == "new_game":
                if new_game_screen:
                    new_game_screen.handle_event(event)

        if current_state == "menu":
            menu_screen.draw()
        elif current_state == "submenu":
            submenu_screen.draw()
        elif current_state == "pokedex":
            if pokedex_screen:
                pokedex_screen.draw()
        elif current_state == "battle":
            if game_instance is None:
                game_instance = Game()
            game_instance.update()
            game_instance.draw(screen)
            if not game_instance.running:
                game_instance = None
                current_state = "menu"
                try:
                    pygame.mixer.music.load("assets/sounds/Main_menu.mp3")
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print("Erreur lors du chargement de Main_menu.mp3", e)
        elif current_state == "load_game":
            if load_game_screen:
                load_game_screen.draw()
        elif current_state == "new_game":
            if new_game_screen:
                new_game_screen.draw()

        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main()
