import pygame
import json
import random
import sys
import os

# --- Chargement des données Pokémon depuis pokemon_data.json ---
with open("pokemon_data.json", "r") as f:
    POKEMON_DATA = json.load(f)

# Dictionnaire simplifié donnant une puissance de base pour quelques attaques courantes.
MOVE_POWER = {
    "tackle": 40,
    "growl": 0,
    "ember": 40,
    "flamethrower": 90,
    "vine-whip": 45,
    "water-gun": 40,
    "scratch": 40,
    "sand-attack": 0,
    # … ajoutez d'autres attaques au besoin
}

# --- Classe Pokémon ---
class Pokemon:
    def __init__(self, data, level=5):
        self.data = data
        self.name = data["name"]
        self.level = level
        # Calcul des HP basé sur la stat PV du JSON et un bonus lié au niveau
        self.max_hp = data["PV"] + level * 2
        self.hp = self.max_hp
        self.attack = data["ATTACK stats"]
        self.defense = data["DEFENS"]
        self.speed = data["VITESSE"]
        self.moves = data["ATTACK list"]
        self.xp = 0  # Expérience initiale
        self.image_path = data.get("local_image_path", "")
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.image.load(self.image_path)
            except Exception as e:
                print(f"Erreur de chargement de l'image {self.image_path}: {e}")
                self.image = None
        else:
            self.image = None

    def get_available_moves(self):
        """Retourne la liste des attaques apprises en fonction du niveau."""
        return [move for move in self.moves if move["level_learned"] <= self.level]

    def is_fainted(self):
        return self.hp <= 0

    def heal(self):
        """Soigne le Pokémon en remettant ses HP au maximum."""
        self.hp = self.max_hp

    def level_up(self):
        """Augmente le niveau et recalcule les stats selon les données de base."""
        self.level += 1
        self.max_hp = self.data["PV"] + self.level * 2
        self.hp = self.max_hp
        self.attack = self.data["ATTACK stats"]
        self.defense = self.data["DEFENS"]
        self.speed = self.data["VITESSE"]

# --- Calcul des dégâts (formule simplifiée) ---
def calculate_damage(attacker, defender, move_name):
    power = MOVE_POWER.get(move_name.lower(), 40)
    if power == 0:
        return 0
    modifier = random.uniform(0.85, 1.0)
    damage = (((2 * attacker.level / 5 + 2) * power * attacker.attack / defender.defense) / 50 + 2) * modifier
    return int(damage)

# --- Affichage d'une barre de vie ---
def draw_hp_bar(surface, x, y, hp, max_hp, width=100, height=10):
    ratio = hp / max_hp
    pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, int(width * ratio), height))

# --- Écran de sélection du starter ---
def starter_selection(screen, font):
    # On propose trois starters classiques
    starters = ["bulbasaur", "charmander", "squirtle"]
    selected = 0
    clock = pygame.time.Clock()
    while True:
        screen.fill((0, 0, 0))
        title = font.render("Sélectionnez votre Pokémon starter :", True, (255, 255, 255))
        screen.blit(title, (150, 100))
        for i, starter in enumerate(starters):
            color = (255, 255, 255)
            if i == selected:
                color = (0, 255, 0)
            text = font.render(starter.upper(), True, color)
            screen.blit(text, (150, 200 + i * 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(starters)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(starters)
                elif event.key == pygame.K_RETURN:
                    return Pokemon(POKEMON_DATA[starters[selected]], level=5)
        clock.tick(30)

# --- Sauvegarde du Pokémon dans pokedex.json ---
def save_to_pokedex(pokemon):
    try:
        with open("pokedex.json", "r") as f:
            try:
                pokedex = json.load(f)
            except json.JSONDecodeError:
                pokedex = {}
    except FileNotFoundError:
        pokedex = {}
    pokedex[pokemon.name] = {
        "level": pokemon.level,
        "xp": pokemon.xp,
        "hp": pokemon.hp,
        "max_hp": pokemon.max_hp,
        "data": pokemon.data
    }
    with open("pokedex.json", "w") as f:
        json.dump(pokedex, f, indent=4)

# --- Fonction de combat simplifié ---
def battle(screen, player_pokemon, enemy_pokemon, font):
    clock = pygame.time.Clock()
    turn = "player" if player_pokemon.speed >= enemy_pokemon.speed else "enemy"
    battle_over = False
    message = ""
    selected_move_index = 0

    while not battle_over:
        screen.fill((0, 0, 0))
        
        # Affichage des images (redimensionnées si disponibles)
        if enemy_pokemon.image:
            enemy_img = pygame.transform.scale(enemy_pokemon.image, (200, 200))
            screen.blit(enemy_img, (400, 50))
        if player_pokemon.image:
            player_img = pygame.transform.scale(player_pokemon.image, (200, 200))
            screen.blit(player_img, (50, 250))
        
        # Affichage des HP et noms
        enemy_hp_text = font.render(f"{enemy_pokemon.name.upper()} HP: {enemy_pokemon.hp}/{enemy_pokemon.max_hp}", True, (255, 255, 255))
        screen.blit(enemy_hp_text, (400, 10))
        draw_hp_bar(screen, 400, 30, enemy_pokemon.hp, enemy_pokemon.max_hp, width=200, height=15)

        player_hp_text = font.render(f"{player_pokemon.name.upper()} HP: {player_pokemon.hp}/{player_pokemon.max_hp}", True, (255, 255, 255))
        screen.blit(player_hp_text, (50, 220))
        draw_hp_bar(screen, 50, 240, player_pokemon.hp, player_pokemon.max_hp, width=200, height=15)

        # Affichage du message d'action
        msg_surface = font.render(message, True, (255, 255, 0))
        screen.blit(msg_surface, (50, 500))

        # Tour du joueur : affichage du menu des attaques
        if turn == "player" and not player_pokemon.is_fainted() and not enemy_pokemon.is_fainted():
            available_moves = player_pokemon.get_available_moves()
            for i, move in enumerate(available_moves):
                color = (255, 255, 255)
                if i == selected_move_index:
                    color = (0, 255, 0)
                move_text = font.render(f"{move['move']}", True, color)
                screen.blit(move_text, (50, 550 + i * 30))

        pygame.display.flip()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if turn == "player" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_move_index = (selected_move_index - 1) % len(player_pokemon.get_available_moves())
                elif event.key == pygame.K_DOWN:
                    selected_move_index = (selected_move_index + 1) % len(player_pokemon.get_available_moves())
                elif event.key == pygame.K_RETURN:
                    available_moves = player_pokemon.get_available_moves()
                    chosen_move = available_moves[selected_move_index]["move"]
                    if random.random() < 0.95:
                        damage = calculate_damage(player_pokemon, enemy_pokemon, chosen_move)
                        enemy_pokemon.hp -= damage
                        message = f"{player_pokemon.name} utilise {chosen_move} et inflige {damage} dégâts !"
                    else:
                        message = f"{player_pokemon.name} utilise {chosen_move} mais rate !"
                    pygame.time.delay(1000)
                    if enemy_pokemon.is_fainted():
                        message = f"{enemy_pokemon.name} est K.O.! Vous gagnez le combat !"
                        battle_over = True
                        break
                    else:
                        turn = "enemy"

        # Tour de l'ennemi
        if turn == "enemy" and not battle_over:
            pygame.time.delay(1000)
            enemy_moves = enemy_pokemon.get_available_moves()
            chosen_move = random.choice(enemy_moves)["move"] if enemy_moves else "tackle"
            if random.random() < 0.95:
                damage = calculate_damage(enemy_pokemon, player_pokemon, chosen_move)
                player_pokemon.hp -= damage
                message = f"{enemy_pokemon.name} utilise {chosen_move} et inflige {damage} dégâts !"
            else:
                message = f"{enemy_pokemon.name} utilise {chosen_move} mais rate !"
            pygame.time.delay(1000)
            if player_pokemon.is_fainted():
                message = f"{player_pokemon.name} est K.O.! Vous perdez..."
                battle_over = True
            else:
                turn = "player"

        clock.tick(30)
    pygame.time.delay(2000)
    return not player_pokemon.is_fainted()  # Renvoie True si le joueur a gagné

# --- Fonction principale ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Système de Combat Pokémon")
    font = pygame.font.SysFont("Arial", 20)

    # --- Sélection du starter ---
    player_pokemon = starter_selection(screen, font)
    save_to_pokedex(player_pokemon)  # Sauvegarde du starter dans pokedex.json

    # Message de confirmation de la sélection
    screen.fill((0, 0, 0))
    select_text = font.render(f"Vous avez choisi {player_pokemon.name.upper()}!", True, (0, 255, 0))
    screen.blit(select_text, (200, 300))
    pygame.display.flip()
    pygame.time.delay(2000)

    # --- Lancement d'un combat simplifié ---
    enemy_name = random.choice(list(POKEMON_DATA.keys()))
    while enemy_name == player_pokemon.name:
        enemy_name = random.choice(list(POKEMON_DATA.keys()))
    enemy_data = POKEMON_DATA[enemy_name]
    enemy_pokemon = Pokemon(enemy_data, level=5)

    battle_result = battle(screen, player_pokemon, enemy_pokemon, font)
    if battle_result:
        # Récompense XP basée sur le niveau de l'ennemi
        xp_reward = enemy_pokemon.level * 10
        player_pokemon.xp += xp_reward

        # Message de XP gagné
        screen.fill((0, 0, 0))
        xp_text = font.render(f"Vous gagnez {xp_reward} XP !", True, (0, 255, 0))
        screen.blit(xp_text, (200, 300))
        pygame.display.flip()
        pygame.time.delay(2000)

        # Vérification d'un éventuel level up (seuil = level * 50 XP)
        if player_pokemon.xp >= player_pokemon.level * 50:
            player_pokemon.xp -= player_pokemon.level * 50
            player_pokemon.level_up()
            level_text = font.render(f"Level Up ! Vous êtes maintenant niveau {player_pokemon.level} !", True, (0, 255, 0))
            screen.fill((0, 0, 0))
            screen.blit(level_text, (150, 300))
            pygame.display.flip()
            pygame.time.delay(2000)

        # Soigner le Pokémon pour le prochain combat
        player_pokemon.heal()

        # Mise à jour du pokedex avec le Pokémon ennemi capturé
        try:
            with open("pokedex.json", "r") as f:
                try:
                    pokedex = json.load(f)
                except json.JSONDecodeError:
                    pokedex = {}
        except FileNotFoundError:
            pokedex = {}
        pokedex[enemy_pokemon.name] = {
            "level": enemy_pokemon.level,
            "xp": enemy_pokemon.xp,
            "hp": enemy_pokemon.hp,
            "max_hp": enemy_pokemon.max_hp,
            "data": enemy_pokemon.data
        }
        with open("pokedex.json", "w") as f:
            json.dump(pokedex, f, indent=4)

        screen.fill((0, 0, 0))
        win_text = font.render(f"Vous avez capturé {enemy_pokemon.name.upper()}!", True, (0, 255, 0))
        screen.blit(win_text, (200, 300))
        pygame.display.flip()
        pygame.time.delay(3000)
    else:
        screen.fill((0, 0, 0))
        lose_text = font.render("Vous avez perdu le combat...", True, (255, 0, 0))
        screen.blit(lose_text, (200, 300))
        pygame.display.flip()
        pygame.time.delay(3000)
    pygame.quit()

if __name__ == "__main__":
    main()
