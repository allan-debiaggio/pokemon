# game/utils.py
import json
import os
import requests
import io
import pygame
from game.settings import SAVE_FILE, SLOT_FILES, POKE_API
from game.pokemon_cache import PokemonCache

def get_pokemon_data(identifier):
    cache = PokemonCache()
    try:
        response = requests.get(f"{POKE_API}{identifier}", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de {identifier} via l'API: {e}")
        cached = cache.get_cached_data(identifier)
        if cached:
            print(f"Utilisation des données en cache pour {identifier}.")
            # Construction d'une structure minimale simulant la réponse de l'API
            fake_data = {
                "name": identifier,
                "id": 0,  # identifiant fictif
                "types": [{"type": {"name": "unknown"}}],
                "stats": [{"stat": {"name": "hp"}, "base_stat": cached["hp"]}],
                "height": 0,
                "weight": 0,
                "sprites": {"front_default": cached["sprite_url"]},
                "species": {"url": ""},
                "moves": []
            }
            return fake_data
        else:
            print(f"Aucune donnée en cache pour {identifier}.")
            return None

def save_game(pokedex, filename=SAVE_FILE, game_name=""):
    image_folder = os.path.join("assets", "poke_image")
    os.makedirs(image_folder, exist_ok=True)
    save_data_pokedex = {}
    for p in pokedex.caught_pokemon:
        next_evo = None
        if p.evolution_data and p.evolution_data['chain'].get('evolves_to'):
            next_evo = p.evolution_data['chain']['evolves_to'][0]['species']['name']
        local_path = os.path.join(image_folder, f"{p.name.lower()}.png")
        if not os.path.exists(local_path):
            try:
                resp = requests.get(p.sprite_url, stream=True, timeout=10)
                if resp.status_code == 200:
                    with open(local_path, 'wb') as f_img:
                        for chunk in resp.iter_content(1024):
                            f_img.write(chunk)
                    print(f"Image de {p.name} téléchargée.")
                else:
                    print(f"Erreur de téléchargement pour {p.name}: code {resp.status_code}")
            except Exception as e:
                print(f"Erreur lors du téléchargement de l'image pour {p.name}: {e}")
        save_data_pokedex[p.name.lower()] = {
            "level": p.level,
            "hp": p.current_hp,
            "sprite_url": p.sprite_url,
            "local_image_path": local_path,
            "evolution": next_evo
        }
    save_data = {"game_name": game_name, "pokedex": save_data_pokedex}
    with open(filename, 'w') as f:
        json.dump(save_data, f, indent=4)
    print("Jeu sauvegardé dans", filename)
    
    # Mise à jour du cache hors ligne avec tous les Pokémon du pokédex
    from game.pokemon_cache import PokemonCache
    cache = PokemonCache()
    for p in pokedex.caught_pokemon:
        cache.update_cache(p)


def load_game(filename=SAVE_FILE):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            if "pokedex" not in data:
                from game.pokedex import Pokedex
                return Pokedex()
            from game.pokedex import Pokedex
            pokedex = Pokedex()
            pokedex.game_name = data.get("game_name", "")
            for name, info in data["pokedex"].items():
                try:
                    from game.pokemon import Pokemon
                    p = Pokemon(name, info["level"])
                except Exception as e:
                    print("Erreur lors du chargement de", name, e)
                    continue
                p.current_hp = info["hp"]
                p.sprite_url = info.get("sprite_url", p.sprite_url)
                local_path = info.get("local_image_path")
                if local_path and os.path.exists(local_path):
                    try:
                        sprite = pygame.image.load(local_path)
                        p.sprite = pygame.transform.scale(sprite, (150, 150))
                    except Exception as e:
                        print("Erreur lors du chargement de l'image locale pour", name, e)
                pokedex.caught_pokemon.append(p)
            return pokedex
    except FileNotFoundError:
        from game.pokedex import Pokedex
        return Pokedex()
