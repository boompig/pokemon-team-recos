import os
import json
from argparse import ArgumentParser

def merge_names():
    all_names = []
    dir = "data/pokemon-names"
    for fname in sorted(os.listdir(dir)):
        if fname.startswith("names-"):
            path = os.path.join(dir, fname)
            with open(path) as f:
                names = json.load(f)
                all_names.extend(names)
    print(len(all_names))
    out_fname = os.path.join(dir, "all-names.json")
    with open(out_fname, "w") as f:
        json.dump(all_names, f, indent=4)


def merge_teams():
    all_teams = []
    dir = "data/teams"
    for fname in sorted(os.listdir(dir)):
        if fname.startswith("oras-"):
            path = os.path.join(dir, fname)
            with open(path) as f:
                teams = json.load(f)
                all_teams.extend(teams)
    print(len(all_teams))
    out_fname = os.path.join(dir, "all-teams.json")
    with open(out_fname, "w") as f:
        json.dump(all_teams, f, indent=4)
    return out_fname


if __name__ == "__main__":
    # fname = merge_names()
    fname = merge_teams()
    print(fname)