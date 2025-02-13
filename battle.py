class Pokemon:
    def __init__(self, name, level):
        data = get_pokemon_data(name)
        self.name = data['name']
        self.level = level
        self.types = [t['type']['name'] for t in data['types']]
        self.stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
        self.hp = self.calculate_hp()
        self.current_hp = self.hp

    def calculate_hp(self):
        base_hp = self.stats['hp']
        return (2 * base_hp * self.level) / 100 + self.level + 10

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0

    def is_fainted(self):
        return self.current_hp == 0

    def use_attack(self, opponent):
        damage = self.calculate_damage(opponent)
        opponent.take_damage(damage)
        print(f"{self.name} attaque {opponent.name} et lui inflige {damage} points de dégâts!")

    def calculate_damage(self, opponent):
        
        base_power = 50

        # multiplicateur de type
        type_multiplier = self.get_type_multiplier(opponent)

        # calcul des dégâts
        damage = ((2 * self.level / 5 + 2) * base_power * (self.stats['attack'] / opponent.stats['defense'])) / 50 + 2
        damage *= type_multiplier
        return int(damage)

    def get_type_multiplier(self, opponent):
        type_chart = {
            "normal" : {"weak":["fignting"],
                    "resistant": [""]},
            "fire": {"weak": ["water", "rock", "ground"], 
                    "resistant": ["grass", "ice","fire","bug","steel","fairy"]},
            "water": {"weak": ["grass", "electric"], 
                    "resistant": ["fire", "ice", " water", "steel"]},
            "electric": {"weak": ["ground"], 
                        "resistant": ["electric", "flying", "steel"]},
            "grass": {"weak": ["fire", "ice", "poison", "flying", "bug"], 
                    "resistant": ["water","electric", "ground", "grass"]},
            "ice": {"weak":["fire","fighting","rock","steel"],
                    "resistant": ["ice"]},
            "fighthing" : {"weak":["flying","psychic","fairy"],
                    "resistant": ["bug","rock","dark"]},
            "poison" : {"weak":["ground","psychic"],
                    "resistant": ["grass","fighting","poison","bug","fairy"]},
            "ground" : {"weak":["water","grass","ice"],
                    "resistant": ["poison","rock"]},
            "flying" : {"weak":["electric","ice","rock"],
                    "resistant": ["grass","fighting","bug"]},
            "psychic" : {"weak":["bug","ghost","dark"],
                    "resistant": ["fighting","psychic"]},
            "bug" : {"weak":["fire","flying","rock"],
                    "resistant": ["grass","fighting","ground"]},
            "rock" : {"weak":["water","grass","fighting","ground","steel"],
                    "resistant": ["normal","fire","poison","flying"]},
            "ghost" : {"weak":["ghost","dark"],
                    "resistant": ["poison","bug"]},
            "dragon" : {"weak":["ice","dragon","fairy"],
                    "resistant": ["fire","water","electric","grass"]},
            "dark" : {"weak":["fighting","bug","fairy"],
                    "resistant": ["ghost","dark"]},
            "steel" : {"weak":["fire","fighting","ground"],
                    "resistant": ["normal","grass","ice","flying","psychic","bug","rock","dragon","steel","fairy"]},
            "fairy" : {"weak":["poison","steel"],
                    "resistant": ["fighting","bug", "dark"]},
        }

        type_multiplier = 1
        for attacker_type in self.types:
            for defender_type in opponent.types:
                if defender_type in type_chart.get(attacker_type, {}).get("weak", []):
                    type_multiplier *= 2
                elif defender_type in type_chart.get(attacker_type, {}).get("resistant", []):
                    type_multiplier *= 0.5
        return type_multiplier
    
    def check_evolution(self):
        if self.evolution_data and self.level >= self.evolution_data["evolution_level"]:
            self.evolve()

    def evolve(self):
        new_name = self.evolution_data["evolves_to"]
        print(f"{self.name} évolue en {new_name}!")
        self.name = new_name
        # Met à jour les stats et les types après l'évolution
        new_data = pokemon_data[new_name]
        self.types = new_data["types"]
        self.stats = new_data["stats"]
    
class Battle:
    def __init__(self, player_pokemon, opponent_pokemon):
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon

    def perform_turn(self):
        # turn player
        self.player_pokemon.use_attack(self.opponent_pokemon)
        if self.opponent_pokemon.is_fainted():
            return "player_wins"

        # turn opponent
        self.opponent_pokemon.use_attack(self.player_pokemon)
        if self.player_pokemon.is_fainted():
            return "opponent_wins"

        return "continue"
    

    # initialisation des pokemons
pikachu = Pokemon("pikachu", 5)
bulbasaur = Pokemon("bulbasaur", 5)

# combat
battle = Battle(pikachu, bulbasaur)

# boucle de combat
while True:
    result = battle.perform_turn()
    if result != "continue":
        print(f"Le combat est terminé ! Résultat : {result}")
        break