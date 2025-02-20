# game/battle.py
import pygame
import random
import math

class Battle:
    def __init__(self, player_pokemon, opponent_pokemon):
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.turn = "player"
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/sounds/Battle.mp3")
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Impossible de charger Battle.mp3", e)

    def perform_attack(self, attacker, defender):
        if random.random() <= 0.1:
            try:
                pygame.mixer.Sound("assets/sounds/Missed_attack.mp3").play()
            except:
                pass
            return f"{attacker.name} rate son attaque!"
        
        base_damage = random.randint(5, 8)
        crit = False
        if random.random() < 0.05:
            base_damage *= 2
            crit = True
        exp_factor = math.exp(0.03 * attacker.level)
        type_multiplier = defender.get_type_effectiveness(self.player_pokemon.types[0], defender.types)
        damage = int(base_damage * exp_factor * type_multiplier)
        defender.take_damage(damage)
        try:
            pygame.mixer.Sound("assets/sounds/Tackle.mp3").play()
        except:
            pass
        message = f"{attacker.name} inflige {damage} dégâts!"
        if crit:
            message += " CRITICAL HIT!"
        if type_multiplier > 1:
            message += " C'est super efficace!"
        elif type_multiplier < 1 and type_multiplier > 0:
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
