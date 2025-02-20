import pygame
import json
import requests
import random
import io
import os
from PIL import Image, ImageSequence

# --- Constantes et initialisations globales ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY  = (128, 128, 128)
BLUE  = (0, 0, 255)

SAVE_FILE = "pokedex.json"
pokeAPI = "https://pokeapi.co/api/v2/pokemon/"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Battle")
font = pygame.font.Font(None, 36)

# --- Système de Menu ---

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
        draw_color = self.hover_color if is_hovered else self.color
        
        pygame.draw.rect(screen, draw_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=10)
        
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
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
                sound = pygame.mixer.Sound("assets/sounds/Button.mp3")
                pygame.mixer.Sound.play(sound)
                self.action()

class Menu:
    def __init__(self, screen, switch_to_battle, switch_to_submenu, switch_to_pokedex):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        self.background = pygame.image.load("assets/images/menu_background.jpg")
        self.buttons = [
            Button(200, 150, 400, 50, "Start", self.font, (255,255,255), (200,200,200), switch_to_battle),
            Button(200, 250, 400, 50, "Pokedex", self.font, (255,255,255), (200,200,200), switch_to_pokedex),
            Button(200, 350, 400, 50, "Quit", self.font, (255,255,255), (200,200,200), lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))),
            Button(200, 450, 400, 50, "Go to SubMenu", self.font, (255,255,255), (200,200,200), switch_to_submenu)
        ]
    
    def draw(self):
        bg = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(bg, (0, 0))
        for button in self.buttons:
            button.draw(self.screen)
    
    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

class SubMenu:
    def __init__(self, screen, switch_to_main_menu):
        self.screen = screen
        self.font = pygame.font.Font(None, 40)
        self.background = pygame.image.load("assets/images/submenu_background.jpg")
        self.buttons = [
            Button(200, 200, 400, 50, "Resume", self.font, (255,255,255), (200,200,200), lambda: print("Resuming game...")),
            Button(200, 300, 400, 50, "Main Menu", self.font, (255,255,255), (200,200,200), switch_to_main_menu)
        ]
    
    def draw(self):
        bg = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(bg, (0, 0))
        for button in self.buttons:
            button.draw(self.screen)
    
    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

class PokedexScreen:
    # Interface autonome pour le menu Pokedex
    def __init__(self, screen, switch_to_main_menu):
        self.screen = screen
        self.switch_to_main_menu = switch_to_main_menu
        self.background = pygame.image.load("assets/images/background_pokedex.png")
        self.font = pygame.font.Font(None, 30)
        try:
            with open(SAVE_FILE, "r") as f:
                content = f.read().strip()
                self.data = json.loads(content) if content else {}
        except FileNotFoundError:
            self.data = {}
        self.back_button = Button(20, 20, 100, 40, "Retour", pygame.font.Font(None, 30),
                                  (200,200,200), (150,150,150), self.switch_to_main_menu)
        self.scroll_offset = 0
    
    def draw(self):
        bg = pygame.transform.scale(self.background, self.screen.get_size())
        self.screen.blit(bg, (0, 0))
        y_offset = 100 - self.scroll_offset
        for key, info in self.data.items():
            card_rect = pygame.Rect(50, y_offset, self.screen.get_width()-100, 120)
            if card_rect.bottom >= 0 and card_rect.top <= self.screen.get_height():
                pygame.draw.rect(self.screen, (255,255,255), card_rect, border_radius=10)
                pygame.draw.rect(self.screen, BLACK, card_rect, 2, border_radius=10)
                try:
                    pokemon_image = pygame.image.load(info["data"]["local_image_path"])
                    pokemon_image = pygame.transform.scale(pokemon_image, (100,100))
                    self.screen.blit(pokemon_image, (card_rect.x+10, card_rect.y+10))
                except Exception as e:
                    print(f"Erreur chargement image {key}: {e}")
                name_text = self.font.render("Nom: " + info["data"]["name"].capitalize(), True, BLACK)
                hp_text = self.font.render("HP: " + str(info["hp"]) + " / " + str(info["max_hp"]), True, BLACK)
                level_text = self.font.render("Niveau: " + str(info.get("level", "N/A")), True, BLACK)
                self.screen.blit(name_text, (card_rect.x+120, card_rect.y+10))
                self.screen.blit(hp_text, (card_rect.x+120, card_rect.y+40))
                self.screen.blit(level_text, (card_rect.x+120, card_rect.y+70))
            y_offset += 140
        self.back_button.draw(self.screen)
    
    def handle_event(self, event):
        self.back_button.handle_event(event)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * 20
            max_scroll = max(0, (100 + len(self.data)*140) - self.screen.get_height())
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

# --- Système de Combat et Sauvegarde ---

def get_pokemon_data(identifier):
    try:
        response = requests.get(f"{pokeAPI}{identifier}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de {identifier}: {e}")
        return None

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
            species_name = chain['species']['name']
            if species_name == self.name.lower():
                if chain.get('evolves_to'):
                    next_evolution = chain['evolves_to'][0]['species']['name']
                    evolution_details = chain['evolves_to'][0].get('evolution_details', [{}])[0]
                    evolution_level = evolution_details.get('min_level') or 20
                    return self.level >= evolution_level, next_evolution
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
        can_evolve, evolution_name = self.can_evolve()
        if can_evolve and evolution_name:
            self.evolve(evolution_name)

    def evolve(self, evolution_name):
        old_name = self.name
        try:
            evolved_data = get_pokemon_data(evolution_name)
            if evolved_data is None:
                return
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
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

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
        for def_type in defender_types:
            if def_type in type_chart[move_type].get("immune", []):
                return 0
            if def_type in type_chart[move_type].get("weak", []):
                multiplier *= 2
            if def_type in type_chart[move_type].get("strong", []):
                multiplier *= 0.5
        return multiplier

class Battle:
    def __init__(self, player_pokemon, opponent_pokemon):
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.turn = "player"
    
    def perform_attack(self, attacker, defender):
        if random.random() <= 0.1:
            return f"{attacker.name} rate son attaque!"
        base_damage = random.randint(5, 8)
        type_multiplier = defender.get_type_effectiveness(self.player_pokemon.types[0], defender.types)
        damage = int(base_damage * type_multiplier)
        defender.take_damage(damage)
        message = f"{attacker.name} inflige {damage} dégats!"
        if type_multiplier > 1:
            message += " C'est super efficace!"
        elif type_multiplier < 1:
            message += " Ce n'est pas très efficace..."
        return message

    def perform_turn(self):
        if self.turn == "player":
            message = self.perform_attack(self.player_pokemon, self.opponent_pokemon)
            self.turn = "opponent"
        else:
            message = self.perform_attack(self.opponent_pokemon, self.player_pokemon)
            self.turn = "player"
        if self.player_pokemon.is_fainted():
            return ("opponent_wins", message)
        elif self.opponent_pokemon.is_fainted():
            exp_gain = self.opponent_pokemon.level * 500
            self.player_pokemon.gain_exp(exp_gain)
            return ("player_wins", message)
        return ("continue", message)

class Pokedex:
    def __init__(self):
        self.seen_pokemon = set()
        self.caught_pokemon = []
    
    def add_pokemon(self, pokemon):
        if not any(p.name == pokemon.name for p in self.caught_pokemon):
            self.seen_pokemon.add(pokemon.name)
            # Création d'une copie pour le pokédex
            captured_pokemon = Pokemon(pokemon.name.lower(), pokemon.level)
            captured_pokemon.exp = pokemon.exp
            captured_pokemon.exp_needed = pokemon.exp_needed
            self.caught_pokemon.append(captured_pokemon)
            print(f"{pokemon.name} a été ajouté au Pokedex!")
        else:
            print(f"Vous avez déjà capturé un {pokemon.name}!")

def start_new_battle(player_pokemon):
    pokemon_ids = list(range(1, 1026))
    random_pokemon_id = random.choice(pokemon_ids)
    opponent_level = get_random_level(player_pokemon.level)
    try:
        opponent = Pokemon(random_pokemon_id, opponent_level)
        return Battle(player_pokemon, opponent)
    except Exception as e:
        print(f"Erreur lors de la création du combat: {e}")
        return None

def get_random_level(base_level, variance=2):
    min_level = max(1, base_level - variance)
    max_level = base_level + variance
    return random.randint(min_level, max_level)

def save_game(pokedex, filename=SAVE_FILE):
    """
    Sauvegarde le pokédex dans un fichier JSON au format souhaité et télécharge les images depuis l'API.
    """
    # S'assurer que le dossier pour les images existe
    image_folder = os.path.join("assets", "poke_image")
    os.makedirs(image_folder, exist_ok=True)

    save_data = {}
    for p in pokedex.caught_pokemon:
        # Téléchargement de l'image depuis l'API
        local_path = os.path.join(image_folder, f"{p.name.lower()}.png")
        try:
            response = requests.get(p.sprite_url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(local_path, 'wb') as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
                print(f"Image de {p.name} téléchargée avec succès.")
            else:
                print(f"Erreur de téléchargement pour {p.name}: code {response.status_code}")
        except Exception as e:
            print(f"Erreur lors du téléchargement de l'image pour {p.name}: {e}")

        # Récupération du niveau d'évolution s'il existe
        if p.evolution_data and p.evolution_data['chain'].get('evolves_to'):
            evo_details = p.evolution_data['chain']['evolves_to'][0].get('evolution_details', [{}])[0]
            evolution_level = evo_details.get('min_level') or 16
        else:
            evolution_level = None

        save_data[p.name.lower()] = {
            "level": p.level,
            "xp": p.exp,
            "hp": p.current_hp,
            "max_hp": p.hp,
            "data": {
                "id": p.id,
                "name": p.name.lower(),
                "height": p.height,
                "weight": p.weight,
                "PV": p.stats.get("hp", 0),
                "ATTACK stats": p.stats.get("attack", 0),
                "DEFENS": p.stats.get("defense", 0),
                "ATTACKSPE": p.stats.get("special-attack", 0),
                "DEFENSE SPE": p.stats.get("special-defense", 0),
                "VITESSE": p.stats.get("speed", 0),
                "ATTACK list": p.moves,
                "TYPE": p.types,
                "EVOLUTION_LEVEL": evolution_level,
                "image_url": p.sprite_url,
                "local_image_path": local_path
            }
        }
    with open(filename, 'w') as f:
        json.dump(save_data, f, indent=4)
    print("Jeu sauvegardé dans", filename)


def load_game(filename=SAVE_FILE):
    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)
            pokedex = Pokedex()
            for name, info in save_data.items():
                pokemon = Pokemon(info["data"]["name"], info["level"])
                pokemon.exp = info["xp"]
                pokemon.current_hp = info["hp"]
                pokedex.caught_pokemon.append(pokemon)
            return pokedex
    except FileNotFoundError:
        return Pokedex()

# --- Classe Game avec pokédex in-game (sélection et sauvegarde) ---
class Game:
    def __init__(self):
        self.running = True
        self.paused = False
        # Tente de charger la sauvegarde ; sinon, crée un nouveau pokédex avec Pikachu
        self.pokedex = load_game() if os.path.exists(SAVE_FILE) else Pokedex()
        if not self.pokedex.caught_pokemon:
            self.pikachu = Pokemon("pikachu", 5)
            self.pokedex.caught_pokemon.append(self.pikachu)
            self.pokedex.seen_pokemon.add(self.pikachu.name)
        else:
            self.pikachu = self.pokedex.caught_pokemon[0]
        battle = start_new_battle(self.pikachu)
        self.battle = battle
        self.opponent_pokemon = battle.opponent_pokemon if battle else None
        try:
            background_path = os.path.join(os.path.dirname(__file__), "assets", "battle_background.gif")
            if not os.path.exists(background_path):
                print(f"Le fichier {background_path} n'existe pas!")
                self.background_frames = None
            else:
                gif = Image.open(background_path)
                self.background_frames = []
                self.current_frame = 0
                for frame in ImageSequence.Iterator(gif):
                    frame_rgb = frame.convert('RGB')
                    frame_str = frame_rgb.tobytes()
                    frame_surface = pygame.image.fromstring(frame_str, frame_rgb.size, 'RGB')
                    frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
                    self.background_frames.append(frame_surface)
                self.frame_delay = gif.info.get('duration', 100) / 1000.0
                self.last_frame_time = pygame.time.get_ticks() / 1000.0
        except Exception as e:
            print(f"Erreur lors du chargement du background: {e}")
            self.background_frames = None
        self.battle_messages = []
        self.message_font = pygame.font.Font(None, 30)
    
    def add_battle_message(self, message):
        self.battle_messages.append(message)
        if len(self.battle_messages) > 3:
            self.battle_messages.pop(0)
    
    def check_game_over(self):
        return all(pokemon.is_fainted() for pokemon in self.pokedex.caught_pokemon)
    
    def heal_all_pokemon(self):
        for pokemon in self.pokedex.caught_pokemon:
            heal_amount = int(pokemon.hp * 0.5)
            pokemon.current_hp = min(pokemon.current_hp + heal_amount, pokemon.hp)
            self.add_battle_message(f"{pokemon.name} récupère {heal_amount} HP!")
    
    def show_pokedex(self):
        """Affiche le pokédex in-game et permet de sélectionner un Pokémon pour le combat."""
        pokedex_running = True
        clock = pygame.time.Clock()
        while pokedex_running:
            screen.fill(WHITE)
            y_offset = 50
            title = font.render("Pokedex", True, BLACK)
            screen.blit(title, (WIDTH//2 - 50, 10))
            pokemon_buttons = []
            for pokemon in self.pokedex.caught_pokemon:
                button_color = GRAY if pokemon.current_hp > 0 else RED
                rect = pygame.Rect(30, y_offset-5, 400, 40)
                pygame.draw.rect(screen, button_color, rect)
                status = "OK" if pokemon.current_hp > 0 else "K.O."
                text = font.render(f"{pokemon.name} - Lv {pokemon.level} - HP: {pokemon.current_hp}/{pokemon.hp} - {status}", True, BLACK)
                screen.blit(text, (50, y_offset))
                pokemon_buttons.append((rect, pokemon))
                y_offset += 50
            back_button = pygame.Rect(650, 500, 120, 40)
            pygame.draw.rect(screen, GRAY, back_button)
            back_text = font.render("Back", True, BLACK)
            screen.blit(back_text, (670, 510))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pokedex_running = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(mouse_pos):
                        pokedex_running = False
                    else:
                        for rect, pokemon in pokemon_buttons:
                            if rect.collidepoint(mouse_pos):
                                if pokemon.current_hp > 0:
                                    self.pikachu = pokemon
                                    pokedex_running = False
                                else:
                                    print(f"{pokemon.name} est K.O. et ne peut pas combattre!")
            pygame.display.flip()
            clock.tick(30)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.paused:
                result, message = self.battle.perform_turn()
                self.add_battle_message(message)
                if result != "continue":
                    if result == "player_wins":
                        self.add_battle_message(f"{self.pikachu.name} gagne!")
                        self.pokedex.add_pokemon(self.opponent_pokemon)
                        self.heal_all_pokemon()
                        battle = start_new_battle(self.pikachu)
                        if battle:
                            self.battle = battle
                            self.opponent_pokemon = battle.opponent_pokemon
                        else:
                            self.running = False
                    elif result == "opponent_wins":
                        self.add_battle_message(f"{self.opponent_pokemon.name} gagne!")
                        if self.check_game_over():
                            self.add_battle_message("Tous vos Pokémon sont K.O.! Game Over!")
                            self.running = False
                        else:
                            self.add_battle_message("Choisissez un autre Pokémon dans le Pokedex!")
                            self.show_pokedex()
                            self.battle = Battle(self.pikachu, self.opponent_pokemon)
            if event.key == pygame.K_f:
                self.add_battle_message("Vous avez fui le combat!")
                self.running = False
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if 650 <= mouse_pos[0] <= 770 and 500 <= mouse_pos[1] <= 540:
                self.running = False
            elif 650 <= mouse_pos[0] <= 770 and 450 <= mouse_pos[1] <= 490:
                self.show_pokedex()
            elif 650 <= mouse_pos[0] <= 770 and 400 <= mouse_pos[1] <= 440:
                save_game(self.pokedex)

    def update(self):
        current_time = pygame.time.get_ticks() / 1000.0
        if self.background_frames and len(self.background_frames) > 0:
            if current_time - self.last_frame_time >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.background_frames)
                self.last_frame_time = current_time

    def draw(self, screen):
        if self.background_frames and len(self.background_frames) > 0:
            screen.blit(self.background_frames[self.current_frame], (0, 0))
        else:
            screen.fill(WHITE)
        def create_rounded_box(width, height, alpha=200, radius=20):
            box = pygame.Surface((width, height), pygame.SRCALPHA)
            box.fill((255,255,255,0))
            pygame.draw.rect(box, (255,255,255,alpha), box.get_rect(), border_radius=radius)
            pygame.draw.rect(box, BLACK, box.get_rect(), 2, border_radius=radius)
            return box
        message_box = create_rounded_box(500, 100)
        screen.blit(message_box, (WIDTH//2 - 250, 10))
        for i, message in enumerate(self.battle_messages):
            message_text = self.message_font.render(message, True, BLACK)
            screen.blit(message_text, (WIDTH//2 - 240, 20 + i * 25))
        player_box = create_rounded_box(300, 100)
        screen.blit(player_box, (50, 480))
        opponent_box = create_rounded_box(300, 80)
        screen.blit(opponent_box, (450, 130))
        button_radius = 15
        quit_box = create_rounded_box(120, 40, alpha=255, radius=button_radius)
        pokedex_box = create_rounded_box(120, 40, alpha=255, radius=button_radius)
        save_box = create_rounded_box(120, 40, alpha=255, radius=button_radius)
        screen.blit(quit_box, (650, 500))
        screen.blit(pokedex_box, (650, 450))
        screen.blit(save_box, (650, 400))
        hp_text = font.render(f"{self.pikachu.name} HP: {self.pikachu.current_hp}/{self.pikachu.hp}", True, BLACK)
        screen.blit(hp_text, (60, 490))
        exp_text = font.render(f"Level: {self.pikachu.level}", True, BLACK)
        screen.blit(exp_text, (60, 520))
        exp_bar_width = 200
        exp_fill = (self.pikachu.exp / self.pikachu.exp_needed) * exp_bar_width
        pygame.draw.rect(screen, BLUE, (60, 550, exp_fill, 20))
        pygame.draw.rect(screen, BLACK, (60, 550, exp_bar_width, 20), 2)
        opponent_info = font.render(f"{self.opponent_pokemon.name} (Lv.{self.opponent_pokemon.level})", True, BLACK)
        screen.blit(opponent_info, (460, 140))
        opp_hp_text = font.render(f"HP: {self.opponent_pokemon.current_hp}/{self.opponent_pokemon.hp}", True, BLACK)
        screen.blit(opp_hp_text, (460, 170))
        if self.pikachu.sprite:
            screen.blit(self.pikachu.sprite, (200, 350))
        if self.opponent_pokemon.sprite:
            screen.blit(self.opponent_pokemon.sprite, (475, 200))
        quit_text = font.render("Quit", True, BLACK)
        pokedex_text = font.render("Pokedex", True, BLACK)
        save_text = font.render("Save", True, BLACK)
        screen.blit(quit_text, (685, 510))
        screen.blit(pokedex_text, (660, 460))
        screen.blit(save_text, (685, 410))
        flee_text = self.message_font.render("F: Fuir", True, BLACK)
        screen.blit(flee_text, (WIDTH - flee_text.get_width() - 10, 10))
        if self.paused:
            pause_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((0,0,0,128))
            screen.blit(pause_overlay, (0,0))
            pause_text = font.render("Paused", True, WHITE)
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))

# --- Boucle principale avec gestion d'états ---
def main():
    clock = pygame.time.Clock()
    current_state = "menu"  # états possibles: "menu", "battle", "pokedex", "submenu"
    game_instance = None

    def switch_to_battle():
        nonlocal current_state
        current_state = "battle"
    def switch_to_submenu():
        nonlocal current_state
        current_state = "submenu"
    def switch_to_main_menu():
        nonlocal current_state
        current_state = "menu"
    def switch_to_pokedex():
        nonlocal current_state
        current_state = "pokedex"

    menu_screen = Menu(screen, switch_to_battle, switch_to_submenu, switch_to_pokedex)
    submenu_screen = SubMenu(screen, switch_to_main_menu)
    pokedex_screen = PokedexScreen(screen, switch_to_main_menu)

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
                pokedex_screen.handle_event(event)
            elif current_state == "battle" and game_instance:
                game_instance.handle_event(event)
        if current_state == "menu":
            menu_screen.draw()
        elif current_state == "submenu":
            submenu_screen.draw()
        elif current_state == "pokedex":
            pokedex_screen.draw()
        elif current_state == "battle":
            if game_instance is None:
                game_instance = Game()
            game_instance.update()
            game_instance.draw(screen)
            if not game_instance.running:
                game_instance = None
                current_state = "menu"
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    main()
