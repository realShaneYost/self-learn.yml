#!/usr/bin/env python3

import argparse
import yaml
from loader import EntityList

def main(args):

    with open(args.file, 'r') as file:
        data = yaml.load(file, Loader=yaml.Loader)

    # Reads/Accesses

    for name in data.entities:
        print(f"Faction: {name}")

    republic = data.entities["Galactic Republic"]
    print("Ships in Galactic Republic:")
    for ship_name in republic.ships:
        print(f"  -{ship_name}")

    ship = data.entities["Galactic Republic"].ships["Venator-class Star Destroyer"]
    print(f"Manufacturer: {ship.manufacturer}")
    print(f"Class: {ship.ship_class}")
    print(f"Armament: {ship.armament}")

    ship = data.entities["Galactic Republic"].ships["Venator-class Star Destroyer"]
    print("Manufacturer:", ship.manufacturer)
    print("Class:", ship.ship_class)
    print("Armament:", ship.armament)

    # Loop

    for faction_name, faction in data.entities.items():
        for ship_name, ship in faction.ships.items():
            if ship.length_meters > 1000:
                print(f"{ship_name} ({faction_name}) is {ship.length_meters}m long")

    # Modifications (Add new ship entry)

    from loader import EntityShip
    new_ship = EntityShip(
        ship_class="Light Freighter",
        length_meters=34.75,
        manufacturer="Corellian Engineering Corporation",
        armament=["Laser cannons"]
    )
    data.entities["Rebel Alliance"].ships["YT-1300 Light Freighter"] = new_ship
    rebel_ships = data.entities["Rebel Alliance"].ships
    if "YT-1300 Light Freighter" not in rebel_ships:
        raise ValueError("Did not find ship")

    # Modifications (Override)

    ship = data.entities["Galactic Empire"].ships["Executor-class Star Dreadnought"]
    ship.length_meters = 20000
    print(ship.length_meters)

    # Modifications (Add new armament)

    ship.armament.append("Death beam")
    print(ship.armament)

    # Conditional
    if "Rebel Alliance" in data.entities:
        faction = data.entities["Rebel Alliance"]
        if "X-Wing (T-65B)" in faction.ships:
            print("X-Wing found in Rebel Alliance")

    # Remove a ship and a faction

    del data.entities["Trade Federation"].ships["C-9979 Landing Craft"]
    del data.entities["Galactic Empire"]

    # Save changes

    with open("output.yaml", "w") as f:
        yaml.dump(data, f, sort_keys=False)

    # ---------------------------------------------------------------------------------------------
    # A star wars introduction to flat list advantages and how to generate one
    # ---------------------------------------------------------------------------------------------

    all_ships = []
    for faction_name, faction in data.entities.items():
        for ship_name, ship in faction.ships.items():
            all_ships.append({
                "faction": faction_name,
                "name": ship_name,
                "class": ship.ship_class,
                "manufacturer": ship.manufacturer,
                "specs": ship
            })

    # NOTE:
    # So why create a flat list? What can it do for me?
    #   -   It's easier to search/filter because it exercises "simple one-pass logic" over the
    #       alternative nested loop structure.
    #   -   Flat lists, in the above example, decouples ships from the hierarchy aka I don't care
    #       about what faction a ship came from.

    for ship in all_ships:
        if "Starfighter" in ship["class"]:
            print(f"{ship['name']} ({ship['faction']}) has torpedoes!")

    # NOTE:
    # So what about sorting? Any benefits to using a flat list? Yes!
    #   -   Sorting is more linear and natural now
    #   -   I can pass this directly to any UI or report
    #   -   No need to sort nested structures and stitch results back together

    sorted_ships = sorted(all_ships, key=lambda s: s["specs"].length_meters, reverse=True)
    for ship in sorted_ships:
        print(f"{ship['name']}: {ship['specs'].length_meters}m")

    # NOTE:
    # How about partial/fuzzy searches like conventional database queries? Yes!
    #   -   Allows your typical database-like searches
    #   -   Human friendly (e.g. search box ui's)
    #   -   Avoid having to crawl/track the context of each match inside nested structures

    query = "freighter"
    matches = [
        ship for ship in all_ships 
        if query.lower() in ship["name"].lower()
    ]
    for ship in matches:
        print(f"{ship['name']} (Faction: {ship['faction']})")

    # NOTE:
    # How about data analysis perks? Yes!
    #   -   Libraries like pandas, numpy and matplotlib work only w/ tabular data so flattening
    #       once allows you to ...
    #           -   Plot ship sizes by fraction in this case
    #           -   Group by ship class
    #           -   Calculate averages, mins, etc more easily
    #   -   Lastly, no extra logic is needed to unwind trees. In otherwords, everything becomes a
    #       row of features

    import pandas as pd
    df = pd.DataFrame([{
        "faction": s["faction"],
        "name": s["name"],
        "length": s["specs"].length_meters,
        "class": s["specs"].ship_class
    } for s in all_ships])
    print(df.describe())

    # NOTE:
    # What about validation and testing? Yes!
    #   -   Allows for centralized quality checks
    #   -   Great for linting, CI/CD validation, or pre-export checks
    #   -   Schema validations are easier in flat form

    for ship in all_ships:
        specs = ship["specs"]
        if not specs.manufacturer:
            print(f"Missing manufacturer: {ship['name']} ({ship['faction']})")

    # NOTE:
    # What about for purposes of indexing, caches, and lookups? Yes!
    #   -   Efficient O(1) lookups
    #   -   Useful for building search APIs, autocomplete, or internel reference maps
    ship_index = {ship["name"]: ship for ship in flat_ships}
    print(ship_index["X-Wing (T-65B)"]["specs"].ship_class)

    # ---------------------------------------------------------------------------------------------
    # So does this make our yaml loader classes setup pointless over flat lists? NO!
    # ---------------------------------------------------------------------------------------------

    # NOTE:
    # IT MIRRORS THE REAL WORLD!
    #
    # I don't just have ships in my example. I have entities (factions) like the Galatic Republic
    # that owns ships with complex specifications. My current loader lets me model that hierarchy
    # cleanly, just like object-oriented design in code. If I wrote all this purely as a flat list
    # I would lose these advantages.

    # NOTE:
    # IT SUPPORTS CLEAN CODE SEPARATION!
    #
    # With my loader classes I can encapsulate behavior, validate data types, provide methods, and
    # add new features. I'm essentially writing python objects to cover more than just YAML
    # deserialization of YAML to dict's. It opens the door for object behavior like ...
    #
    # if ship.has_proton_torpedoes()

    # NOTE:
    # I CAN STILL FLATTEN WHEN I NEED TO!
    #
    # I'm not choosing between either/or. I'm choosing Loader + Class-based structure for modeling
    # and flat list for operations (search, sort, export). I could add a method in EntityList 
    # loader class called to_flat_ship_list().
    #
    #     class EntityList:
    #         ...
    #         def to_flat_ship_list(self):
    #             return [
    #                 {
    #                     "faction": faction_name,
    #                     "name": ship_name,
    #                     "specs": ship
    #                 }
    #                 for faction_name, faction in self.entities.items()
    #                 for ship_name, ship in faction.ships.items()
    #             ]
    #     
    #     # Example Usage:
    #     flat_ships = data.to_flat_ship_list()
    #     for ship in flat_ships:
    #         print(f"{ship['name']} ({ship['faction']}): {ship['specs'].ship_class}")
    #
    # By providing this above method I'm saying "I will model this richly, but I'll expose a flat
    # view when I need performance, simplicity, or tabular tools.".
    # WARN: Have not added to_flat_ship_list(self) to class. Just documenting the idea here.

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="StarWars Themed Yaml Loader")
    parser.add_argument( "-f", "--file", type=str, default="../data.yaml", help="yaml file")
    args = parser.parse_args()
    main(args)
