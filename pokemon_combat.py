from pokeload import get_all_pokemons
import random
from pprint import pprint
import os


def get_player_profile(pokemon_list):
    return {
        "name": input("¿Cómo te llamas? "),
        "pokemon_inventory": [random.choice(pokemon_list) for a in range(3)],
        "combats": 0,
        "pokeballs": 3,
        "pociones": 2   # in spanish so the function confirm_object() makes sense
    }


def any_pokemon_lives(player_profile):
    return sum([pokemon["current_health"] for pokemon in player_profile["pokemon_inventory"]]) > 0


def health_bars(player_pokemon, enemy_pokemon):
    lenght = 20
    player_ratio = player_pokemon["current_health"]/player_pokemon["base_health"]
    enemy_ratio = enemy_pokemon["current_health"]/enemy_pokemon["base_health"]
    print("{} [{}{}] {}/{}".format(player_pokemon["name"],
                                   "#"*int(lenght*player_ratio), " "*int((lenght-lenght*player_ratio)),
                                   player_pokemon["current_health"], player_pokemon["base_health"]))
    print("{} [{}{}] {}/{}\n".format(enemy_pokemon["name"],
                                     "#" * int(lenght * enemy_ratio), " " * int((lenght - lenght * enemy_ratio)),
                                     enemy_pokemon["current_health"], enemy_pokemon["base_health"]))


def available_attacks(pokemon):
    attacks = []
    for i in range(len(pokemon["attacks"])):
        if pokemon["level"] >= pokemon["attacks"][i]["min_lvl"]:
            attacks.append(pokemon["attacks"][i])
    return attacks


def damage_multiplier(attack, attacked):
    # Damage is 1.25 effective if attacked it's weak type, 0.75 if it's strong. If it's immune: damage = 0
    weak = {
        "agua": ["electrico", "planta"],
        "bicho": ["fuego", "roca", "veneno", "volador"],
        "dragon": ["dragon", "hielo"],
        "electrico": ["tierra"],
        "fantasma": ["fantasma"],
        "fuego": ["agua", "roca", "tierra"],
        "hielo": ["fuego", "lucha", "roca"],
        "lucha": ["psiquico", "Volador"],
        "normal": ["lucha"],
        "planta": ["bicho", "fuego", "hielo", "veneno", "volador"],
        "psiquico": ["bicho"],
        "roca": ["agua", "lucha", "planta", "tierra"],
        "tierra": ["agua", "hielo", "planta"],
        "veneno": ["bicho, psiquico", "tierra"],
        "volador": ["electrico", "hielo", "roca"],
        "hada": ["veneno"],
        "acero": ["fuego", "lucha", "tierra"]
              }

    strong = {
        "agua": ["agua", "fuego", "hielo"],
        "bicho": ["lucha", "planta", "Tierra"],
        "dragon": ["agua", "electrico", "fuego", "planta"],
        "electrico": ["electrico", "volador"],
        "fantasma": ["veneno"],
        "fuego": ["bicho", "fuego", "planta"],
        "hielo": ["hielo"],
        "lucha": ["bicho", "roca"],
        "normal": [],
        "planta": ["agua", "electrico", "planta", "tierra"],
        "psiquico": ["lucha", "psiquico"],
        "roca": ["fuego", "normal", "veneno", "volador"],
        "tierra": ["roca", "veneno"],
        "veneno": ["lucha", "planta", "veneno"],
        "volador": ["bicho", "lucha", "planta"],
        "hada": ["bicho", "lucha"],
        "acero": ["acero", "bicho", "dragon", "fantasma", "hielo", "normal",
                  "planta", "psiquico", "roca", "siniesto","volador"]
              }

    immune = {
        "agua": [],
        "bicho": [],
        "dragon": [],
        "electrico": [],
        "fantasma": ["lucha", "normal"],
        "fuego": [],
        "hielo": [],
        "lucha": [],
        "normal": ["fantasma"],
        "planta": [],
        "psiquico": ["fantasma"],
        "roca": [],
        "tierra": ["electrico"],
        "veneno": [],
        "volador": ["tierra"],
        "hada": ["dragon"],
        "acero": ["veneno"]
    }

    if attack["damage"] != 0:
        for type in attacked["type"]:
            if attack["type"] in weak[type]:
                print("¡{} es efectivo!".format(attack["name"]))
                return int(attack["damage"]*1.25)
            elif attack["type"] in strong[type]:
                print("¡{} no es efectivo!".format(attack["name"]))
                return int(attack["damage"]*0.75)
            elif attack["type"] in immune[type]:
                print("¡{} no hace efecto!".format(attack["name"]))
                return 0
    return attack["damage"]


def player_attack(player_pokemon, enemy_pokemon):
    health_bars(player_pokemon, enemy_pokemon)
    print("Selecciona un ataque: ")
    # Only some attacks are available depending on Pokémon's level
    player_attacks = available_attacks(player_pokemon)
    for i in range(len(player_attacks)):
        print("[{}] {} - TIPO: {} - DAÑO: {}".format(i+1, player_attacks[i]["name"],
                                                     player_attacks[i]["type"],
                                                     player_attacks[i]["damage"]))

    attack = None
    while not attack:
        try:
            attack = player_attacks[int(input())-1]
        except (ValueError, IndexError):
            print("¡Opción inválida! Escoge un ataque:")

    print("¡{} ha usado {}!".format(player_pokemon["name"], attack["name"]))
    player_pokemon["n_attacks"] += 1    # used to asign exp at the end of battle

    enemy_pokemon["current_health"] -= damage_multiplier(attack, enemy_pokemon)
    if enemy_pokemon["current_health"] <= 0:
        enemy_pokemon["current_health"] = 0
        health_bars(player_pokemon, enemy_pokemon)
        print("¡{} ha derrotado a {}!".format(player_pokemon["name"], enemy_pokemon["name"]))


def enemy_attack(enemy_pokemon, player_pokemon):
    health_bars(player_pokemon, enemy_pokemon)
    enemy_attacks = available_attacks(enemy_pokemon)
    attack = random.choice(enemy_attacks)
    print("¡{} ha usado {}!".format(enemy_pokemon["name"], attack["name"]))
    player_pokemon["current_health"] -= damage_multiplier(attack, player_pokemon)
    if player_pokemon["current_health"] <= 0:
        player_pokemon["current_health"] = 0
        health_bars(player_pokemon, enemy_pokemon)
        print("¡{} ha derrotado a {}!".format(enemy_pokemon["name"], player_pokemon["name"]))


def action_selection(player_pokemon, enemy_pokemon, player_profile):
    health_bars(player_pokemon, enemy_pokemon)
    action = input("¿Qué deseas hacer?\n"
                   "[A]tacar\n"
                   "[P]okeball\n"
                   "Poción de 50 de [V]ida\n"
                   "[C]ambiar Pokémon\n").upper()
    while action not in ["A", "P", "V", "C"]:
        action = input("¡Opción inválida! ¿Qué deseas hacer?\n"
                       "[A]tacar\n"
                       "[P]okeball\n"
                       "Poción de 50 de [V]ida\n"
                       "[C]ambiar Pokémon\n").upper()

    if action == "A":
        player_attack(player_pokemon, enemy_pokemon)

    elif action == "P":
        pokeball(player_profile, enemy_pokemon, player_pokemon)

    elif action == "V":
        add_health(player_pokemon, enemy_pokemon, player_profile)

    elif action == "C":
        return pokemon_selection(player_profile, enemy_pokemon)

    return player_pokemon


def fight(player_profile, enemy_pokemon):
    win = None
    player_pokemon = pokemon_selection(player_profile, enemy_pokemon)
    player_profile["combats"] += 1

    os.system("cls")
    print("-----EMPIEZA LA BATALLA Nº{}-----".format(player_profile["combats"]))
    print("{} VS {}".format(pokemon_stats(player_pokemon), pokemon_stats(enemy_pokemon)))

    while any_pokemon_lives(player_profile):
        player_pokemon = action_selection(player_pokemon, enemy_pokemon, player_profile)    # player turn
        if enemy_pokemon["current_health"] == 0:
            win = True
            break

        enemy_attack(enemy_pokemon, player_pokemon)
        if player_pokemon["current_health"] == 0:
            player_pokemon = pokemon_selection(player_profile, enemy_pokemon)
    battle_end(player_profile, enemy_pokemon, win)


def battle_end(player_profile, enemy_pokemon, win):
    print("-----FIN DE LA BATALLA-----")

    # Por cada ataque de un pokemon se suman de entre 1 a 5 de exp
    exp(player_profile)
    if win:
        item_lottery(player_profile)


def item_lottery(player_profile):
    objects = ["pokeball", "poción"]
    prize = None
    if random.randint(1, 100) <= 33:    # there is a 33% chance the player might get an object
        prize = random.choice(objects)

    if prize:
        if prize == "pokeball":
            player_profile["pokeballs"] += 1
        else:
            player_profile["pociones"] += 1
        print("¡Has obtenido una {}!".format(prize))


def exp(player_profile):
    for pokemon in player_profile["pokemon_inventory"]:
        if pokemon["n_attacks"] > 0:
            for i in range(pokemon["n_attacks"]):
                pokemon["current_exp"] += random.randint(5, 10)     # Pokémon gets between 5 and 10 exp for each attack
            pokemon["n_attacks"] = 0

            # Pokémon levels up when reaches 15 exp
            if pokemon["current_exp"] >= 15:
                pokemon["level"] += pokemon["current_exp"]//15
                pokemon["current_exp"] = pokemon["current_exp"] % 15
                print("¡{} ha subido a nivel {}!".format(pokemon["name"], pokemon["level"]))


def confirm_object(item, player_profile, player_pokemon, enemy_pokemon):
    if player_profile[item] > 0:
        action = input("Tienes {} {}. ¿Quieres usar una? [S/N]\n".format(player_profile[item], item)).upper()
        while action not in ["S", "N"]:
            action = input("¡Opción inválida! Tienes {} {}. ¿Quieres usar una? [S/N]\n"
                           .format(player_profile[item], item)).upper()
        return action
    else:  # has 0 potions or pokeballs
        print("¡No tienes {}!".format(item))
        action_selection(player_pokemon, enemy_pokemon, player_profile)


def pokeball(player_profile, enemy_pokemon, player_pokemon):
    action = confirm_object("pokeballs", player_profile, player_pokemon, enemy_pokemon)

    if action == "S":
        # function follows that prob(%) = 0.0245*1.0427^(100-hp) * 100
        if player_profile["pokeballs"] > 0:
            player_profile["pokeballs"] -= 1
        prob = int(0.027*(1.0416**(100-enemy_pokemon["current_health"]))*100)
        if random.randint(1, 100) <= prob:
            player_profile["pokemon_inventory"].append(enemy_pokemon.copy())
            print("¡La captura ha sido efectiva!")
            enemy_pokemon["current_health"] = 0     # so line 348 works
        else:
            print("¡La captura no ha sido efectiva!")
        return player_pokemon

    else:   # does not want to use pokeball
        action_selection(player_pokemon, enemy_pokemon, player_profile)


def add_health(player_pokemon, enemy_pokemon, player_profile):
    # If user has potions, it restores 50 hp
    action = confirm_object("pociones", player_profile, player_pokemon, enemy_pokemon)

    def heal_display(player_profile):
        print("¿A qué Pokémon quieres curar?")
        for i in range(len(player_profile["pokemon_inventory"])):
            print("[{}] {}".format(i + 1, pokemon_stats(player_profile["pokemon_inventory"][i])))

    if action == "S":
        if player_profile["pociones"] > 0:
            player_profile["pociones"] -= 1
        heal_display(player_profile)
        healed_pokemon = None
        try:
            healed_pokemon = player_profile["pokemon_inventory"][int(input())-1]
        except ValueError:
            while healed_pokemon not in range(len(player_profile["pokemon_inventory"])):
                try:
                    print("¡Opción no válida!")
                    heal_display(player_profile)
                    healed_pokemon = player_profile["pokemon_inventory"][int(input())-1]
                except ValueError:
                    pass

        healed_pokemon["current_health"] += 50
        if healed_pokemon["current_health"] > 100:
            healed_pokemon["current_health"] = 100
        print("¡{} se ha curado!".format(pokemon_stats(healed_pokemon)))
        action_selection(player_pokemon, enemy_pokemon, player_profile)

    else:   # does not want to use potion
        action_selection(player_pokemon, enemy_pokemon, player_profile)


def pokemon_stats(pokemon):
    return "{} | LVL {} | HP {}/{}".format(pokemon["name"],
                                           pokemon["level"],
                                           pokemon["current_health"],
                                           pokemon["base_health"])


def pokemon_selection(player_profile, enemy_pokemon):
    print("¡Tu enemigo es {}! ¿Qué pokemon escoges para combatir? ".format(pokemon_stats(enemy_pokemon)))
    in_field_pokemon = None

    def display():
        for i in range(len(player_profile["pokemon_inventory"])):
            print("[{}] {}".format(i + 1, pokemon_stats(player_profile["pokemon_inventory"][i])))

    display()

    while not in_field_pokemon:
        try:
            in_field_pokemon = player_profile["pokemon_inventory"][int(input("")) - 1]
            while in_field_pokemon["current_health"] == 0:
                print("¡{} no tiene vida! Selecciona otro Pokémon: \n".format(in_field_pokemon["name"]))
                display()
                in_field_pokemon = player_profile["pokemon_inventory"][int(input("")) - 1]
            return in_field_pokemon
        except (ValueError, IndexError):
            print("¡Opción inválida! Escoge un Pokémon: ")


def enemy_level(enemy_pokemon, player_profile):
    player_pokemon_lvls = []
    random_upgrade = 5
    for pokemon in player_profile["pokemon_inventory"]:
        player_pokemon_lvls.append(pokemon["level"])
    player_pokemon_lvls.sort(reverse=True)
    enemy_pokemon["level"] = random.randint(1, player_pokemon_lvls[0]+random_upgrade)


def main():
    # Load 1st gen Pokémon and set player inventory
    pokemon_list = get_all_pokemons()
    player_profile = get_player_profile(pokemon_list)

    enemy_pokemon = random.choice(pokemon_list)
    # Enemy Pokémon might be 5 levels up than the Pokémon with most level of the player
    enemy_level(enemy_pokemon, player_profile)

    # Game start
    while any_pokemon_lives(player_profile):
        fight(player_profile, enemy_pokemon)
        if enemy_pokemon["current_health"] == 0:
            enemy_pokemon = random.choice(pokemon_list)
            enemy_level(enemy_pokemon, player_profile)
    print("Has perdido en el combate nº {}.".format(player_profile["combats"]))


if __name__ == "__main__":
    main()
