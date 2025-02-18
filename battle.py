import pygame
import requests
import random
import io
import json
import os
from PIL import Image, ImageSequence

SAVE_FILE = "save.json"

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon Battle")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)


font = pygame.font.Font(None, 36)

# API Pokemon
pokeAPI = "https://pokeapi.co/api/v2/pokemon/"

def get_pokemon_data(identifier):
    try:
        response = requests.get(f"{pokeAPI}{identifier}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur: Impossible de trouver le Pokémon {identifier}")
            raise ValueError(f"Pokémon {identifier} not found")
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion: {e}")
        raise 
class Pokemon:
    def __init__(self, identifier, level):
        data = get_pokemon_data(identifier)
        self.name = data['name'].capitalize()
        self.id = str(data['id'])
        self.level = level
        self.exp = 0
        self.exp_needed = level * 100
        self.types = [t['type']['name'] for t in data['types']]
        self.stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
        self.hp = self.calculate_hp()
        self.current_hp = self.hp
        self.sprite_url = data['sprites']['front_default']
        self.sprite = self.load_sprite()
        self.evolution_data = self.get_evolution_data(data)

    def get_evolution_data(self, data):
        try:
            species_url = data['species']['url']
            species_data = requests.get(species_url).json()
            evolution_url = species_data['evolution_chain']['url']
            evolution_data = requests.get(evolution_url).json()
            return evolution_data
        except requests.RequestException as e:  
            print(f"Erreur réseau lors de la récupération des données d'évolution: {e}")
            return None
        except KeyError as e:  
            print(f"Données d'évolution manquantes: {e}")
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
                    
                    # if min_level is specified, use that level
                    if evolution_details.get('min_level'):
                        evolution_level = evolution_details['min_level']
                    else:
                        # else, use a default level based on the current level
                        evolution_level = 20
                    
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
        print(f"{self.name} leveled up to level {self.level}!")

        can_evolve, evolution_name = self.can_evolve()
        if can_evolve and evolution_name:
            self.evolve(evolution_name)

    def evolve(self, evolution_name):
        old_name = self.name
        try:
            evolved_data = get_pokemon_data(evolution_name)
            current_hp_percent = self.current_hp / self.hp
            
            # Update Pokemon data
            self.name = evolved_data['name'].capitalize()
            self.types = [t['type']['name'] for t in evolved_data['types']]
            self.stats = {stat['stat']['name']: stat['base_stat'] for stat in evolved_data['stats']}
            self.sprite_url = evolved_data['sprites']['front_default']
            self.sprite = self.load_sprite()
            self.evolution_data = self.get_evolution_data(evolved_data)
            
            # Recalculate HP with new stats
            old_max_hp = self.hp
            old_current_hp = self.current_hp
            self.hp = self.calculate_hp()
            self.current_hp = int((old_current_hp / old_max_hp) * self.hp)
            
            print(f"Congratulations! {old_name} evolved into {self.name}!")
            print(f"New base stats: {self.stats}")
        except Exception as e:
            print(f"Evolution error: {e}")

    def load_sprite(self):
        try:
            response = requests.get(self.sprite_url)
            if response.status_code == 200:
                image_data = io.BytesIO(response.content)
                image = pygame.image.load(image_data)
                return pygame.transform.scale(image, (150, 150))
        except Exception as e:
            print(f"Erreur de chargement du sprite pour {self.name}: {e}")
            return pygame.Surface((150, 150)) 

    def calculate_hp(self):
        base_hp = self.stats['hp']
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
        type_messages = []
        
        for def_type in defender_types:
            current_multiplier = 1.0
            
            # check for immunities
            if def_type in type_chart[move_type].get("immune", []):
                print(f"{def_type} is immune to {move_type}!")
                return 0
                
            # check for weaknesses
            if def_type in type_chart[move_type].get("weak", []):
                current_multiplier *= 2
                print(f"x2 contre {def_type}")
                
            # check for strengths
            if def_type in type_chart[move_type].get("strong", []):
                current_multiplier *= 0.5
                type_messages.append(f"x0.5 contre {def_type}")
                
            multiplier *= current_multiplier
        
        # display messages for effectiveness
        if multiplier >= 4:
            print("It's ultra effective!")
        elif multiplier == 2:
            print("It's super effective!")
        elif multiplier == 0.5:
            print("It's not very effective...")
        elif multiplier == 0.25:
            print("It's barely effective...")
        
        if type_messages:
            print(" + ".join(type_messages))
            
        return multiplier

class Battle:
    def __init__(self, player_pokemon, opponent_pokemon):
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.turn = "player"  

    def perform_attack(self, attacker, defender):
        if random.random() <= 0.1:
            return f"{attacker.name} missed their attack!"
        
        base_damage = random.randint(5, 8)
        type_multiplier = self.get_type_multiplier(defender)
        damage = int(base_damage * type_multiplier)
        defender.take_damage(damage)
        message = f"{attacker.name} deals {damage} damage!"
        if type_multiplier > 1:
            message += " It's super effective!"
        elif type_multiplier < 1:
            message += " It's not very effective..."
        return message

    def perform_turn(self):
        if self.turn == "player":
            message = self.perform_attack(self.player_pokemon, self.opponent_pokemon)
            self.turn = "opponent"
        else:
            message = self.perform_attack(self.opponent_pokemon, self.player_pokemon)
            self.turn = "player"

        # Check Pokémon Status
        if self.player_pokemon.is_fainted():
            return ("opponent_wins", message)
        elif self.opponent_pokemon.is_fainted():
            exp_gain = self.opponent_pokemon.level * 500
            self.player_pokemon.gain_exp(exp_gain)
            return ("player_wins", message)
        return ("continue", message)

    def get_type_multiplier(self, defender):
        return defender.get_type_effectiveness(self.player_pokemon.types[0], defender.types)

class Pokedex:
    def __init__(self):
        self.seen_pokemon = set()
        self.caught_pokemon = []
    
    def add_pokemon(self, pokemon):
        if not any(p.name == pokemon.name for p in self.caught_pokemon):
            self.seen_pokemon.add(pokemon.name)
            captured_pokemon = Pokemon(pokemon.name.lower(), pokemon.level)
            captured_pokemon.exp = pokemon.exp
            captured_pokemon.exp_needed = pokemon.exp_needed
            self.caught_pokemon.append(captured_pokemon)
            print(f"{pokemon.name} was added to the Pokedex!")
        else:
            print(f"You already caught a {pokemon.name}!")

def start_new_battle(player_pokemon):
    """Creates a new fight with an opponent adapted to the player's level"""
    pokemon_ids = list(range(1, 1026))
    random_pokemon_id = random.choice(pokemon_ids)
    opponent_level = get_random_level(player_pokemon.level)
    try:
        opponent = Pokemon(random_pokemon_id, opponent_level)
        return Battle(player_pokemon, opponent)
    except Exception as e:
        print(f"Error creating the fight: {e}")
        return None

def get_random_level(base_level, variance=2):
    """Generates a random level close to the base level"""
    min_level = max(1, base_level - variance)
    max_level = base_level + variance
    return random.randint(min_level, max_level)

def save_game(pokedex, filename=SAVE_FILE):
    save_data = {
        'caught_pokemon': [
            {
                'name': p.name.lower(),
                'level': p.level,
                'exp': p.exp,
                'current_hp': p.current_hp,
                'evolution_data': p.evolution_data 
            } for p in pokedex.caught_pokemon
        ]
    }
    with open(filename, 'w') as f:
        json.dump(save_data, f)

def load_game(filename=SAVE_FILE):
    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)
            pokedex = Pokedex()
            for p_data in save_data['caught_pokemon']:
                pokemon = Pokemon(p_data['name'], p_data['level'])
                pokemon.exp = p_data['exp']
                pokemon.current_hp = p_data['current_hp']
                pokedex.caught_pokemon.append(pokemon)
            return pokedex
    except FileNotFoundError:
        return Pokedex()

class Game:
    def __init__(self):
        self.running = True 
        self.pokedex = Pokedex()
        self.pikachu = Pokemon("pikachu", 5)
        self.pokedex.caught_pokemon.append(self.pikachu)
        self.pokedex.seen_pokemon.add(self.pikachu.name)
        
        battle = start_new_battle(self.pikachu)
        self.opponent_pokemon = battle.opponent_pokemon  
        self.battle = battle

        # Load animated GIF background
        try:
            background_path = os.path.join(os.path.dirname(__file__), "assets", "battle_background.gif")
            if not os.path.exists(background_path):
                print(f"Le fichier {background_path} n'existe pas!")
                self.background_frames = None
                return

            gif = Image.open(background_path)
            self.background_frames = []
            self.current_frame = 0
            
            # Convert each frame of GIF to pygame surface
            for frame in ImageSequence.Iterator(gif):
                frame_rgb = frame.convert('RGB')
                frame_str = frame_rgb.tobytes()
                frame_surface = pygame.image.fromstring(frame_str, frame_rgb.size, 'RGB')
                frame_surface = pygame.transform.scale(frame_surface, (WIDTH, HEIGHT))
                self.background_frames.append(frame_surface)
                
            self.frame_delay = gif.info.get('duration', 100) / 1000.0
            self.last_frame_time = pygame.time.get_ticks() / 1000.0
            
        except Exception as e:
            print(f"Error loading background: {e}")
            self.background_frames = None

        self.battle_messages = []
        self.message_font = pygame.font.Font(None, 30) 

    def add_battle_message(self, message):
        self.battle_messages.append(message)
        if len(self.battle_messages) > 3: 
            self.battle_messages.pop(0)

    def check_game_over(self):
        """Vérifie si tous les Pokémon du joueur sont K.O."""
        return all(pokemon.is_fainted() for pokemon in self.pokedex.caught_pokemon)

    def show_pokedex(self):
        pokedex_running = True
        while pokedex_running:
            screen.fill(WHITE)
            y_offset = 50
            title = font.render("Pokedex", True, BLACK)
            screen.blit(title, (WIDTH//2 - 50, 10))
            
            pokemon_buttons = []
            for pokemon in self.pokedex.caught_pokemon:
                button_color = GRAY if pokemon.current_hp > 0 else RED
                button_rect = pygame.draw.rect(screen, button_color, (30, y_offset-5, 400, 40))
                if pokemon.current_hp > 0:
                    pokemon_buttons.append((button_rect, pokemon))
                status = "OK" if pokemon.current_hp > 0 else "K.O."
                text = font.render(f"{pokemon.name} - Niveau {pokemon.level} - HP: {pokemon.current_hp}/{pokemon.hp} - {status}", True, BLACK)
                screen.blit(text, (50, y_offset))
                y_offset += 50
            
            back_button = pygame.draw.rect(screen, GRAY, (650, 500, 120, 40))
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
                        for button, pokemon in pokemon_buttons:
                            if button.collidepoint(mouse_pos):
                                if pokemon.current_hp > 0:
                                    self.pikachu = pokemon
                                    self.battle = Battle(self.pikachu, self.opponent_pokemon)
                                    pokedex_running = False
                                else:
                                    print(f"{pokemon.name} is KO and cannot fight!")
                        
            pygame.display.flip()

    def heal_all_pokemon(self):
        """Heals all Pokémon in the Pokedex for 50% of their HP"""
        for pokemon in self.pokedex.caught_pokemon:
            heal_amount = pokemon.hp * 0.5  
            pokemon.current_hp = min(pokemon.current_hp + int(heal_amount), pokemon.hp)
            self.add_battle_message(f"{pokemon.name} recovered {int(heal_amount)} HP!")

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            current_time = pygame.time.get_ticks() / 1000.0
            
            # Animate the background
            if self.background_frames and len(self.background_frames) > 0:
                if current_time - self.last_frame_time >= self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.background_frames)
                    self.last_frame_time = current_time
                screen.blit(self.background_frames[self.current_frame], (0, 0))
            else:
                screen.fill(WHITE)

            # Create rounded boxes with alpha channel
            def create_rounded_box(width, height, alpha=200, radius=20):
                box = pygame.Surface((width, height), pygame.SRCALPHA)
                box.fill((255, 255, 255, 0))  # Transparent background
                pygame.draw.rect(box, (255, 255, 255, alpha), box.get_rect(), border_radius=radius)
                pygame.draw.rect(box, (0, 0, 0, 255), box.get_rect(), 2, border_radius=radius)
                return box

            # Message box
            message_box = create_rounded_box(500, 100)
            screen.blit(message_box, (WIDTH//2 - 250, 10))

            # Display battle messages
            for i, message in enumerate(self.battle_messages):
                message_text = self.message_font.render(message, True, BLACK)
                screen.blit(message_text, (WIDTH//2 - 240, 20 + i * 25))

            # Player info box
            player_box = create_rounded_box(300, 100)
            screen.blit(player_box, (50, 480))

            # Opponent info box
            opponent_box = create_rounded_box(300, 80)
            screen.blit(opponent_box, (450, 130))

            # Buttons box with smaller radius
            button_radius = 15
            quit_box = create_rounded_box(120, 40, alpha=255, radius=button_radius)
            pokedex_box = create_rounded_box(120, 40, alpha=255, radius=button_radius)
            save_box = create_rounded_box(120, 40, alpha=255, radius=button_radius)

            screen.blit(quit_box, (650, 500))
            screen.blit(pokedex_box, (650, 450))
            screen.blit(save_box, (650, 400))

            # Player Pokémon info
            hp_text = font.render(f"{self.pikachu.name} HP: {self.pikachu.current_hp}/{self.pikachu.hp}", True, BLACK)
            screen.blit(hp_text, (60, 490))  
            exp_text = font.render(f"Level: {self.pikachu.level}", True, BLACK)
            screen.blit(exp_text, (60, 520))  
            exp_bar = pygame.Surface((150, 5))
            exp_bar.fill(GRAY)
            exp_fill = (self.pikachu.exp / self.pikachu.exp_needed) * 200
            pygame.draw.rect(screen, BLUE, (60, 550, exp_fill, 20))  
            pygame.draw.rect(screen, BLACK, (60, 550, 200, 20), 2)  

            # Opponent Pokémon info
            opponent_info = font.render(f"{self.opponent_pokemon.name} (Lvl.{self.opponent_pokemon.level})", True, BLACK)
            screen.blit(opponent_info, (460, 140))
            hp_text = font.render(f"HP: {self.opponent_pokemon.current_hp}/{self.opponent_pokemon.hp}", True, BLACK)
            screen.blit(hp_text, (460, 170))

            # Display Pokémon sprites
            if self.pikachu.sprite:
                screen.blit(self.pikachu.sprite, (200, 350))
            if self.opponent_pokemon.sprite:
                screen.blit(self.opponent_pokemon.sprite, (475, 200))

            # Quit button
            pygame.draw.rect(screen, WHITE, (650, 500, 120, 40), border_radius=15)
            pygame.draw.rect(screen, BLACK, (650, 500, 120, 40), 2, border_radius=15)  
            
            # Pokedex button
            pygame.draw.rect(screen, WHITE, (650, 450, 120, 40), border_radius=15)
            pygame.draw.rect(screen, BLACK, (650, 450, 120, 40), 2, border_radius=15)  
            
            # Save button
            pygame.draw.rect(screen, WHITE, (650, 400, 120, 40), border_radius=15)
            pygame.draw.rect(screen, BLACK, (650, 400, 120, 40), 2, border_radius=15)  
            
            # Button texts
            quit_text = font.render("Quit", True, BLACK)
            pokedex_text = font.render("Pokedex", True, BLACK)
            save_text = font.render("Save", True, BLACK)
            screen.blit(quit_text, (685, 510))
            screen.blit(pokedex_text, (660, 460))
            screen.blit(save_text, (685, 410))

            # manage events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:  # SPACE for attack
                        result, message = self.battle.perform_turn()
                        self.add_battle_message(message)
                        
                        if result != "continue":
                            if result == "player_wins":
                                self.add_battle_message(f"{self.pikachu.name} wins!")
                                self.pokedex.add_pokemon(self.opponent_pokemon)

                                self.heal_all_pokemon()
                                self.battle = start_new_battle(self.pikachu)
                                if self.battle:
                                    self.opponent_pokemon = self.battle.opponent_pokemon
                                else:
                                    self.running = False
                            elif result == "opponent_wins":
                                self.add_battle_message(f"{self.opponent_pokemon.name} wins!")
                                if self.check_game_over():
                                    self.add_battle_message("All your Pokemon are KO! Game Over!")
                                    self.running = False
                                else:
                                    self.add_battle_message("Choose another Pokemon from your Pokedex!")
                                    self.show_pokedex()
                                    self.battle = Battle(self.pikachu, self.opponent_pokemon)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if 650 <= mouse_pos[0] <= 770 and 500 <= mouse_pos[1] <= 540:
                        self.running = False
                    elif 650 <= mouse_pos[0] <= 770 and 450 <= mouse_pos[1] <= 490:
                        self.show_pokedex()
                    elif 650 <= mouse_pos[0] <= 770 and 400 <= mouse_pos[1] <= 440:
                        save_game(self.pokedex)
                        print("Game saved!")
            
            pygame.display.flip()
            clock.tick(30)  # Limite à 30 FPS

    def cleanup(self):
        """Clean up resources before exiting"""
        pygame.quit()

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    finally:
        game.cleanup()