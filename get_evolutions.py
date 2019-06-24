from argparse import ArgumentParser
import os
import json
import requests
# from pprint import pprint


url = "https://pokeapi.co/api/v2/pokemon/"
species_url = "https://pokeapi.co/api/v2/pokemon-species/"


def get_evolutions(mon: str):
    r1 = requests.get(url + mon.lower())
    if r1.status_code != 200:
        raise RuntimeError("Failed to get pokemon with name %s" % mon)
    j1 = r1.json()
    r2 = requests.get(species_url + j1['species']['name'])
    j2 = r2.json()
    r3 = requests.get(j2["evolution_chain"]["url"])
    j3 = r3.json()
    return j3["chain"]


def get_raw():
    parser = ArgumentParser()
    parser.add_argument("list", help="File containing a list of pokemon")
    parser.add_argument("out_dir")
    parser.add_argument("--start", default="A")
    args = parser.parse_args()

    assert os.path.exists(args.list)

    with open(args.list) as f:
        contents = json.load(f)
        if isinstance(contents, list):
            mons = contents
        else:
            mons = []
            for k, v in contents.items():
                mons.extend(v)

    chains = {}
    fname = os.path.join(args.out_dir, "evo-chain-{}.json".format(args.start))

    def save_results():
        with open(fname, "w") as f:
            json.dump(chains, f, indent=4, sort_keys=True)

    for mon in sorted(mons):
        if mon < args.start:
            continue
        if " " in mon:
            mon = mon.split(" ")[0]
        elif mon == "Tailow":
            # spelling mistake
            mon = "Taillow"
        print(mon)
        evos = get_evolutions(mon)
        chains[mon] = evos
        save_results()


def print_chain(link, level):
    name = link["species"]["name"]
    if level == 0:
        # print(name)
        pass
    else:
        # print("\t" * level + "-> " + name)
        pass

    children = []
    for child in link["evolves_to"]:
        c = print_chain(child, level + 1)
        children.append(c)
    return {name: children}


def get_mons_from_chain(chain, mons):
    for mon, children in chain.items():
        mons.add(mon)
        for child in children:
            get_mons_from_chain(child, mons)


if __name__ == "__main__":
    # get_raw()
    parser = ArgumentParser()
    parser.add_argument("in_file")
    parser.add_argument("out_dir")
    args = parser.parse_args()

    master_chain = {}

    with open(args.in_file) as f:
        contents = json.load(f)
        for mon, v in contents.items():
            d = print_chain(v, 0)
            master_chain.update(d)
    # pprint(master_chain)

    # figure out all the mons
    mons = set([])
    get_mons_from_chain(master_chain, mons)

    fname = os.path.join(args.out_dir, "evo-chain-parsed.json")
    with open(fname, 'w') as f:
        json.dump({
            'chain': master_chain,
            'pokemon': list(sorted(mons))
        }, f, indent=4, sort_keys=True)