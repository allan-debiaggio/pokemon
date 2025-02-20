# game/settings.py

# Dimensions de la fenêtre
WIDTH = 800
HEIGHT = 600

# Couleurs (en RGB)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY   = (128, 128, 128)
BLUE   = (0, 0, 255)

# Fichiers de sauvegarde
SAVE_FILE = "pokedex.json"
SLOT_FILES = {
    1: "save_slot_1.json",
    2: "save_slot_2.json",
    3: "save_slot_3.json"
}

# URL de l'API Pokémon
POKE_API = "https://pokeapi.co/api/v2/pokemon/"
