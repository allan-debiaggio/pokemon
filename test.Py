import os
import json
import requests
import pokebase as pb

images_folder = os.path.join("assets", "poke_image")
os.makedirs(images_folder, exist_ok=True)

pokemon_data = {}

for i in range(1, 1026):
    try:
        pokemon = pb.pokemon(i)
        
        image_url = None
        if hasattr(pokemon.sprites.other, 'official_artwork') and pokemon.sprites.other.official_artwork.front_default:
            image_url = pokemon.sprites.other.official_artwork.front_default
        elif pokemon.sprites.front_default:
            image_url = pokemon.sprites.front_default
        
        local_image_path = None
        
        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                local_image_path = os.path.join(images_folder, f"{pokemon.name}.png")
                with open(local_image_path, "wb") as img_file:
                    img_file.write(response.content)
                print(f"Téléchargement de l'image de {pokemon.name} réussi.")
            else:
                print(f"Erreur {response.status_code} lors du téléchargement de l'image de {pokemon.name}.")
        else:
            print(f"Aucune image disponible pour {pokemon.name}.")
        
        pokemon_data[pokemon.name] = {
            "id": pokemon.id,
            "name": pokemon.name,
            "height": pokemon.height,
            "weight": pokemon.weight,
            "types": [t.type.name for t in pokemon.types],
            "image_url": image_url,
            "local_image_path": local_image_path
        }
        
    except Exception as e:
        print(f"Erreur lors du traitement du Pokémon n°{i} : {e}")

with open("pokemon_data.json", "w", encoding="utf-8") as json_file:
    json.dump(pokemon_data, json_file, indent=4, ensure_ascii=False)

print("Création du JSON et téléchargement des images terminés.")
