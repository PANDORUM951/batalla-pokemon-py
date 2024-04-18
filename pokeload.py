from requests_html import HTMLSession
import pickle

pokemon_base = {
    "name": "",
    "type": None,
    "level": 1,
    "current_exp": 0,
    "base_health": 100,
    "current_health": 100,
    "n_attacks": 0
}

BASE_URL = "https://www.pokexperto.net/index2.php?seccion=nds/nationaldex/movimientos_nivel&pk="


def get_min_atk_lvl(attack_item):
    try:
        return int(attack_item.find("th")[1].text)
    except ValueError:
        return None


def get_pokemon(index, session):
    # Get url
    pokemon_url = "{}{}".format(BASE_URL, index)
    pokemon_page = session.get(pokemon_url)

    # Get Pokémon stats
    new_pokemon = pokemon_base.copy()

    new_pokemon["name"] = pokemon_page.html.find(".mini", first=True).text.split("\n")[0]

    new_pokemon["type"] = []
    for img in pokemon_page.html.find(".pkmain", first=True).find(".bordeambos", first=True).find("img"):
        new_pokemon["type"].append(img.attrs["alt"])

    new_pokemon["attacks"] = []

    for attack_item in pokemon_page.html.find(".pkmain")[-1].find("tr .check3"):
        attack = {
            "name": attack_item.find("td", first=True).find("a", first=True).text,
            "type": attack_item.find("td")[1].find("img", first=True).attrs["alt"],
            "damage": int(attack_item.find("td")[3].text.replace("--", "0")),
            "min_lvl": get_min_atk_lvl(attack_item)
        }
        if attack["min_lvl"]:
            new_pokemon["attacks"].append(attack)

    print(new_pokemon["name"])

    return new_pokemon


def get_all_pokemons():
    try:
        print("Cargando lista de pokemons...")
        with open("pokefile.pkl", "rb") as pokefile:
            all_pokemons = pickle.load(pokefile)
    except FileNotFoundError:
        print("¡Archivo no encontrado! Cargando de internet...")
        all_pokemons = []
        session = HTMLSession()
        for i in range(151):
            all_pokemons.append(get_pokemon(i+1, session))
            print("*", end="")

        with open("pokefile.pkl", "wb") as pokefile:
            pickle.dump(all_pokemons, pokefile)
        print("\n¡Todos los pokemons han sido cargados!")

    print("¡Lista de pokemons cargada!")
    return all_pokemons


def main():
    for pokemon in get_all_pokemons():
        print(pokemon)


if __name__ == "__main__":
    main()
