import os
import json
import requests
import pokebase as pb

def find_evolution_level(species_name, chain):
    if chain.species.name == species_name:
        if chain.evolves_to:
            levels = []
            for evo in chain.evolves_to:
                for detail in evo.evolution_details:
                    if detail.min_level is not None:
                        levels.append(detail.min_level)
            return min(levels) if levels else None
        return None
    for evo in chain.evolves_to:
        result = find_evolution_level(species_name, evo)
        if result is not None:
            return result
    return None

images_folder = os.path.join("assets", "poke_image")
os.makedirs(images_folder, exist_ok=True)

pokemon_data = {}

for i in range(1, 51):
    try:
        p = pb.pokemon(i)
        species = pb.pokemon_species(p.name)
        
        chain_data = pb.evolution_chain(species.evolution_chain.id)
        evolution_level = find_evolution_level(species.name, chain_data.chain)
        
        stats = {stat.stat.name: stat.base_stat for stat in p.stats}
        
        moves_list = []
        for m in p.moves:
            level_learned = None
            for detail in m.version_group_details:
                if detail.move_learn_method.name == "level-up" and detail.level_learned_at > 0:
                    if level_learned is None or detail.level_learned_at < level_learned:
                        level_learned = detail.level_learned_at
            if level_learned is not None:
                moves_list.append({
                    "move": m.move.name,
                    "level_learned": level_learned
                })
        
        image_url = None
        if hasattr(p.sprites.other, 'official_artwork') and p.sprites.other.official_artwork.front_default:
            image_url = p.sprites.other.official_artwork.front_default
        elif p.sprites.front_default:
            image_url = p.sprites.front_default
        
        local_image_path = None
        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                local_image_path = os.path.join(images_folder, f"{p.name}.png")
                with open(local_image_path, "wb") as img_file:
                    img_file.write(response.content)
                print(f"Image de {p.name} téléchargée.")
            else:
                print(f"Erreur {response.status_code} pour l'image de {p.name}.")
        else:
            print(f"Aucune image trouvée pour {p.name}.")
        
        pokemon_data[p.name] = {
            "id": p.id,
            "name": p.name,
            "height": p.height,
            "weight": p.weight,
            "PV": stats.get("hp"),
            "ATTACK stats": stats.get("attack"),
            "DEFENS": stats.get("defense"),
            "ATTACKSPE": stats.get("special-attack"),
            "DEFENSE SPE": stats.get("special-defense"),
            "VITESSE": stats.get("speed"),
            "ATTACK list": moves_list,
            "TYPE": [t.type.name for t in p.types],
            "EVOLUTION_LEVEL": evolution_level,
            "image_url": image_url,
            "local_image_path": local_image_path
        }
        
        print(f"Pokémon {p.name} traité.")
        
    except Exception as e:
        print(f"Erreur lors du traitement du Pokémon n°{i}: {e}")

with open("pokemon_data.json", "w", encoding="utf-8") as json_file:
    json.dump(pokemon_data, json_file, indent=4, ensure_ascii=False)

print("JSON créé et images téléchargées avec succès.")
