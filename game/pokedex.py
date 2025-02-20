# game/pokedex.py
import pygame

class Pokedex:
    def __init__(self):
        self.seen_pokemon = set()
        self.caught_pokemon = []
        self.game_name = ""

    def add_pokemon(self, pokemon):
        try:
            pygame.mixer.Sound("assets/sounds/Capture.mp3").play()
        except Exception as e:
            pass
        if not any(p.name == pokemon.name for p in self.caught_pokemon):
            self.seen_pokemon.add(pokemon.name)
            from .pokemon import Pokemon
            captured = Pokemon(pokemon.name.lower(), pokemon.level)
            captured.exp = pokemon.exp
            captured.exp_needed = pokemon.exp_needed
            self.caught_pokemon.append(captured)
            print(f"{pokemon.name} a été ajouté au Pokedex!")
            # Mise à jour du cache hors ligne
            from .pokemon_cache import PokemonCache
            cache = PokemonCache()
            cache.update_cache(pokemon)
        else:
            print(f"Vous avez déjà capturé un {pokemon.name}!")
