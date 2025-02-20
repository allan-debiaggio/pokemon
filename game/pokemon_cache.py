# game/pokemon_cache.py
import os
import json

class PokemonCache:
    CACHE_FILE = "pokemon_data.json"

    def __init__(self):
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement du cache: {e}")
                return {}
        return {}

    def save_cache(self):
        with open(self.CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=4)

    def get_cached_data(self, identifier):
        key = str(identifier).lower()
        return self.cache.get(key)

    def update_cache(self, pokemon):
        key = pokemon.name.lower()
        data = {
            "level": pokemon.level,
            "hp": pokemon.hp,
            "sprite_url": pokemon.sprite_url,
            "local_image_path": f"assets\\poke_image\\{pokemon.name.lower()}.png",
            "evolution": None
        }
        if pokemon.evolution_data:
            chain = pokemon.evolution_data.get("chain")
            if chain and chain.get("evolves_to"):
                data["evolution"] = chain["evolves_to"][0]["species"]["name"]
        self.cache[key] = data
        self.save_cache()
