# data take from here: https://www.smogon.com/forums/threads/oras-in-game-tier-list-read-post-324.3523089/

# from pprint import pprint
import os
import json

dir = "data/in-game-tier-list"
in_fname = os.path.join(dir, "raw.txt")

tiers = {}
tier = None

with open(in_fname) as f:
    for line in f:
        line = line.strip()
        if line == "":
            continue
        if line.startswith("-"):
            tier = line[1]
            tiers[tier] = []
        else:
            tiers[tier].append(line)

out_fname = os.path.join(dir, "parsed.json")
with open(out_fname, "w") as f:
    json.dump(tiers, f, indent=4, sort_keys=True)
print(out_fname)

# pprint(tiers)
