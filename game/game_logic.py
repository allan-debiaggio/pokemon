# game/game_logic.py
import os
import random
import pygame
import math
from PIL import Image, ImageSequence
from game.battle import Battle
from game.pokedex import Pokedex
from game.pokemon import Pokemon
from game.utils import save_game
from game.settings import WIDTH, HEIGHT, WHITE, BLACK, SLOT_FILES, GREEN, YELLOW, RED

def start_new_battle(player_pokemon):
    ids = list(range(1, 1026))
    rand_id = random.choice(ids)
    opp_level = get_random_level(player_pokemon.level)
    try:
        opponent = Pokemon(rand_id, opp_level)
        return Battle(player_pokemon, opponent)
    except Exception as e:
        print(f"Erreur lors de la création du combat via l'API: {e}")
        # Utilisation des données en cache pour l'ennemi
        from game.pokemon_cache import PokemonCache
        cache = PokemonCache()
        if cache.cache:
            cached_keys = list(cache.cache.keys())
            random_key = random.choice(cached_keys)
            cached_data = cache.cache[random_key]
            print(f"Utilisation des données en cache pour l'ennemi: {random_key}")
            try:
                # Tenter de recréer un Pokémon via get_pokemon_data (qui utilisera le cache si besoin)
                opponent = Pokemon(random_key, opp_level)
            except Exception as ex:
                # En cas d'échec, on crée manuellement un Pokémon minimal
                opponent = Pokemon.__new__(Pokemon)
                opponent.name = random_key.capitalize()
                opponent.id = 0
                opponent.level = opp_level
                opponent.exp = 0
                opponent.exp_needed = opp_level * 100
                opponent.types = [{"type": {"name": "unknown"}}]
                opponent.stats = {"hp": int(cached_data["hp"])}
                opponent.height = 0
                opponent.weight = 0
                opponent.hp = int(cached_data["hp"])
                opponent.current_hp = opponent.hp
                opponent.sprite_url = cached_data["sprite_url"]
                try:
                    opponent.sprite = pygame.image.load(cached_data["local_image_path"])
                    opponent.sprite = pygame.transform.scale(opponent.sprite, (150, 150))
                except Exception as load_ex:
                    opponent.sprite = pygame.Surface((150, 150))
                opponent.evolution_data = None
                opponent.moves = []
            return Battle(player_pokemon, opponent)
        else:
            print("Aucune donnée en cache n'est disponible.")
            return None

def get_random_level(base_level, variance=2):
    return random.randint(max(1, base_level - variance), base_level + variance)

def new_game(slot, game_name):
    from game.pokedex import Pokedex
    filename = SLOT_FILES[slot]
    pokedex = Pokedex()
    pikachu = Pokemon("pikachu", 5)
    pokedex.caught_pokemon.append(pikachu)
    pokedex.seen_pokemon.add(pikachu.name)
    pokedex.game_name = game_name
    save_game(pokedex, filename, game_name)
    from game.game_logic import Game
    return Game(save_file=filename)

class Game:
    def __init__(self, save_file="pokedex.json"):
        self.save_file = save_file
        self.running = True
        self.paused = False
        from game.utils import load_game
        if os.path.exists(save_file):
            self.pokedex = load_game(filename=save_file)
        else:
            from game.pokedex import Pokedex
            self.pokedex = Pokedex()
        if not self.pokedex.caught_pokemon:
            self.pikachu = Pokemon("pikachu", 5)
            self.pokedex.caught_pokemon.append(self.pikachu)
            self.pokedex.seen_pokemon.add(self.pikachu.name)
        else:
            self.pikachu = self.pokedex.caught_pokemon[0]
        battle = start_new_battle(self.pikachu)
        self.battle = battle
        self.opponent_pokemon = battle.opponent_pokemon if battle else None

        # Chargement du background animé (GIF) pour le combat
        try:
            bg_path = os.path.join(os.path.dirname(__file__), "assets", "battle_background.gif")
            if not os.path.exists(bg_path):
                print(f"Le fichier {bg_path} n'existe pas!")
                self.background_frames = None
            else:
                gif = Image.open(bg_path)
                self.background_frames = []
                self.current_frame = 0
                for frame in ImageSequence.Iterator(gif):
                    fr_rgb = frame.convert('RGB')
                    fr_str = fr_rgb.tobytes()
                    fr_surface = pygame.image.fromstring(fr_str, fr_rgb.size, 'RGB')
                    fr_surface = pygame.transform.scale(fr_surface, (WIDTH, HEIGHT))
                    self.background_frames.append(fr_surface)
                self.frame_delay = gif.info.get('duration', 100) / 1000.0
                self.last_frame_time = pygame.time.get_ticks() / 1000.0
        except Exception as e:
            print(f"Erreur lors du chargement du background: {e}")
            self.background_frames = None

        self.battle_messages = []
        self.message_font = pygame.font.Font(None, 30)
        self.battle_music_pos = 0

    def add_battle_message(self, msg):
        self.battle_messages.append(msg)
        if len(self.battle_messages) > 3:
            self.battle_messages.pop(0)

    def check_game_over(self):
        return all(p.is_fainted() for p in self.pokedex.caught_pokemon)

    def heal_all_pokemon(self):
        for p in self.pokedex.caught_pokemon:
            heal = int(p.hp * 0.5)
            p.current_hp = min(p.current_hp + heal, p.hp)
            self.add_battle_message(f"{p.name} récupère {heal} HP!")

    def show_pokedex(self):
        self.battle_music_pos = pygame.mixer.music.get_pos() / 1000.0
        try:
            pygame.mixer.music.load("assets/sounds/pokedex.mp3")
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Erreur lors du chargement de la musique du Pokédex: {e}")
        from game.pokedex_screen import PokedexScreen
        pscreen = PokedexScreen(pygame.display.get_surface(), self.pokedex, lambda: None)
        selected = pscreen.run()
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load("assets/sounds/Battle.mp3")
            pygame.mixer.music.play(-1, start=self.battle_music_pos)
        except Exception as e:
            print(f"Erreur lors du chargement de la musique de combat: {e}")
        if selected:
            self.pikachu = selected
            print(f"Vous avez sélectionné {self.pikachu.name} pour combattre.")
            if self.battle:
                self.battle.player_pokemon = self.pikachu

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.paused and self.battle:
                result, msg = self.battle.perform_turn()
                self.add_battle_message(msg)
                if result != "continue":
                    if result == "player_wins":
                        self.add_battle_message(f"{self.pikachu.name} gagne!")
                        self.pokedex.add_pokemon(self.opponent_pokemon)
                        self.heal_all_pokemon()
                        new_battle = start_new_battle(self.pikachu)
                        if new_battle:
                            self.battle = new_battle
                            self.opponent_pokemon = new_battle.opponent_pokemon
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
                            if self.opponent_pokemon and self.pikachu:
                                from game.battle import Battle
                                self.battle = Battle(self.pikachu, self.opponent_pokemon)
            if event.key == pygame.K_f:
                try:
                    pygame.mixer.Sound("assets/sounds/Run_away.mp3").play()
                except:
                    pass
                self.add_battle_message("Vous avez fui le combat!")
                self.running = False
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if 650 <= pos[0] <= 770 and 500 <= pos[1] <= 540:
                self.running = False
            elif 650 <= pos[0] <= 770 and 450 <= pos[1] <= 490:
                self.show_pokedex()
            elif 650 <= pos[0] <= 770 and 400 <= pos[1] <= 440:
                save_game(self.pokedex, self.save_file)

    def update(self):
        now = pygame.time.get_ticks() / 1000.0
        if self.background_frames:
            if now - self.last_frame_time >= self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.background_frames)
                self.last_frame_time = now

    def draw(self, screen):
        if self.background_frames:
            screen.blit(self.background_frames[self.current_frame], (0, 0))
        else:
            screen.fill(WHITE)

        def box(w, h, alpha=200, r=20):
            b = pygame.Surface((w, h), pygame.SRCALPHA)
            b.fill((255, 255, 255, 0))
            pygame.draw.rect(b, (255, 255, 255, alpha), b.get_rect(), border_radius=r)
            pygame.draw.rect(b, BLACK, b.get_rect(), 2, border_radius=r)
            return b

        mbox = box(500, 100)
        screen.blit(mbox, (WIDTH // 2 - 250, 10))
        for i, m in enumerate(self.battle_messages):
            screen.blit(self.message_font.render(m, True, BLACK), (WIDTH // 2 - 240, 20 + i * 25))

        pbox = box(300, 100)
        screen.blit(pbox, (50, 480))
        obox = box(300, 80)
        screen.blit(obox, (450, 130))
        br = 15
        qbox = box(120, 40, alpha=255, r=br)
        pbox2 = box(120, 40, alpha=255, r=br)
        sbox = box(120, 40, alpha=255, r=br)
        screen.blit(qbox, (650, 500))
        screen.blit(pbox2, (650, 450))
        screen.blit(sbox, (650, 400))

        hp_ratio = self.pikachu.current_hp / self.pikachu.hp
        hp_color = GREEN if hp_ratio > 0.5 else YELLOW if hp_ratio > 0.2 else RED
        font = pygame.font.Font(None, 36)
        screen.blit(font.render(f"{self.pikachu.name} HP: {self.pikachu.current_hp}/{self.pikachu.hp}", True, BLACK), (60, 490))
        screen.blit(font.render(f"Level: {self.pikachu.level}", True, BLACK), (60, 520))
        ebar_w = 200
        efill = (self.pikachu.exp / self.pikachu.exp_needed) * ebar_w
        pygame.draw.rect(screen, hp_color, (60, 550, efill, 20))
        pygame.draw.rect(screen, BLACK, (60, 550, ebar_w, 20), 2)

        if self.opponent_pokemon:
            screen.blit(font.render(f"{self.opponent_pokemon.name} (Lv.{self.opponent_pokemon.level})", True, BLACK), (460, 140))
            screen.blit(font.render(f"HP: {self.opponent_pokemon.current_hp}/{self.opponent_pokemon.hp}", True, BLACK), (460, 170))
            if self.opponent_pokemon.sprite:
                screen.blit(self.opponent_pokemon.sprite, (475, 200))
        if self.pikachu.sprite:
            screen.blit(self.pikachu.sprite, (200, 350))

        screen.blit(font.render("Quit", True, BLACK), (685, 510))
        screen.blit(font.render("Pokedex", True, BLACK), (660, 460))
        screen.blit(font.render("Save", True, BLACK), (685, 410))
        f_text = self.message_font.render("F: Fuir", True, BLACK)
        screen.blit(f_text, (WIDTH - f_text.get_width() - 10, 10))
