# game/pokemon.py
import pygame
import requests
import io
from game.utils import get_pokemon_data

class Pokemon:
    def __init__(self, identifier, level):
        data = get_pokemon_data(identifier)
        if data is None:
            raise ValueError("Impossible de charger les données du Pokémon")
        self.name = data['name'].capitalize()
        self.id = data['id']
        self.level = level
        self.exp = 0
        self.exp_needed = level * 100
        self.types = [t['type']['name'] for t in data['types']]
        self.stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
        self.height = data.get('height', 0)
        self.weight = data.get('weight', 0)
        self.hp = self.calculate_hp()
        self.current_hp = self.hp
        self.sprite_url = data['sprites']['front_default']
        self.sprite = self.load_sprite()
        self.evolution_data = self.get_evolution_data(data)
        self.moves = []
        for m in data.get("moves", []):
            details = m.get("version_group_details", [])
            level_learned = details[0].get("level_learned_at", 0) if details else 0
            self.moves.append({
                "move": m["move"]["name"],
                "level_learned": level_learned
            })

    def get_evolution_data(self, data):
        try:
            species_url = data['species']['url']
            species_data = requests.get(species_url).json()
            evolution_url = species_data['evolution_chain']['url']
            evolution_data = requests.get(evolution_url).json()
            return evolution_data
        except Exception as e:
            print(f"Données d'évolution indisponibles: {e}")
            return None

    def can_evolve(self):
        if not self.evolution_data:
            return False, None
        chain = self.evolution_data['chain']
        while chain:
            if chain['species']['name'] == self.name.lower():
                if chain.get('evolves_to'):
                    next_evo = chain['evolves_to'][0]['species']['name']
                    evo_details = chain['evolves_to'][0].get('evolution_details', [{}])[0]
                    evo_level = evo_details.get('min_level') or 20
                    return self.level >= evo_level, next_evo
                return False, None
            if chain.get('evolves_to'):
                chain = chain['evolves_to'][0]
            else:
                break
        return False, None

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_needed:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_needed
        self.exp_needed = self.level * 100
        old_hp = self.hp
        self.hp = self.calculate_hp()
        self.current_hp += (self.hp - old_hp)
        print(f"{self.name} passe au niveau {self.level}!")
        try:
            pygame.mixer.Sound("assets/sounds/Level_up.mp3").play()
        except:
            pass
        can_evolve, evo = self.can_evolve()
        if can_evolve and evo:
            self.evolve(evo)

    def evolve(self, evolution_name):
        old_name = self.name
        try:
            evolved_data = get_pokemon_data(evolution_name)
            if evolved_data is None:
                return
            try:
                pygame.mixer.Sound("assets/sounds/Evolution.mp3").play()
            except:
                pass
            old_current_hp = self.current_hp
            old_hp = self.hp
            self.name = evolved_data['name'].capitalize()
            self.types = [t['type']['name'] for t in evolved_data['types']]
            self.stats = {stat['stat']['name']: stat['base_stat'] for stat in evolved_data['stats']}
            self.sprite_url = evolved_data['sprites']['front_default']
            self.sprite = self.load_sprite()
            self.evolution_data = self.get_evolution_data(evolved_data)
            self.hp = self.calculate_hp()
            self.current_hp = int((old_current_hp / old_hp) * self.hp)
            print(f"Félicitations ! {old_name} évolue en {self.name}!")
        except Exception as e:
            print(f"Erreur lors de l'évolution: {e}")

    def load_sprite(self):
        try:
            response = requests.get(self.sprite_url, timeout=5)
            if response.status_code == 200:
                image_data = io.BytesIO(response.content)
                image = pygame.image.load(image_data)
                return pygame.transform.scale(image, (150, 150))
        except Exception as e:
            print(f"Erreur de chargement du sprite pour {self.name}: {e}")
        return pygame.Surface((150, 150))

    def calculate_hp(self):
        base_hp = self.stats.get("hp", 0)
        return int((2 * base_hp * self.level) / 100 + self.level + 10)

    def take_damage(self, damage):
        self.current_hp = max(self.current_hp - damage, 0)

    def is_fainted(self):
        return self.current_hp == 0

    def get_type_effectiveness(self, move_type, defender_types):
        type_chart = {
            "normal": {"strong": ["fighting"], "immune": ["ghost"]},
            "fire": {"strong": ["water", "rock", "ground"], "weak": ["grass", "ice", "bug", "steel"]},
            "water": {"strong": ["grass", "electric"], "weak": ["fire", "ground", "rock"]},
            "electric": {"strong": ["ground"], "weak": ["water", "flying"]},
            "grass": {"strong": ["fire", "ice", "poison", "flying", "bug"], "weak": ["water", "ground", "rock"]},
            "ice": {"strong": ["fire", "fighting", "rock", "steel"], "weak": ["grass", "ground", "flying", "dragon"]},
            "fighting": {"strong": ["flying", "psychic", "fairy"], "weak": ["normal", "ice", "rock", "dark", "steel"]},
            "poison": {"strong": ["ground", "psychic"], "weak": ["grass", "fairy"]},
            "ground": {"strong": ["water", "grass", "ice"], "weak": ["fire", "electric", "poison", "rock", "steel"]},
            "flying": {"strong": ["electric", "ice", "rock"], "weak": ["grass", "fighting", "bug"]},
            "psychic": {"strong": ["bug", "ghost", "dark"], "weak": ["fighting", "poison"]},
            "bug": {"strong": ["fire", "flying", "rock"], "weak": ["grass", "psychic", "dark"]},
            "rock": {"strong": ["water", "grass", "fighting", "ground", "steel"], "weak": ["fire", "ice", "flying", "bug"]},
            "ghost": {"strong": ["ghost", "dark"], "weak": ["psychic", "ghost"]},
            "dragon": {"strong": ["ice", "dragon", "fairy"], "weak": ["dragon"]},
            "dark": {"strong": ["fighting", "bug", "fairy"], "weak": ["psychic", "ghost"]},
            "steel": {"strong": ["fire", "fighting", "ground"], "weak": ["ice", "rock", "fairy"]},
            "fairy": {"strong": ["poison", "steel"], "weak": ["fighting", "dragon", "dark"]}
        }
        multiplier = 1.0
        for dt in defender_types:
            if dt in type_chart[move_type].get("immune", []):
                return 0
            if dt in type_chart[move_type].get("weak", []):
                multiplier *= 2
            if dt in type_chart[move_type].get("strong", []):
                multiplier *= 0.5
        return multiplier
