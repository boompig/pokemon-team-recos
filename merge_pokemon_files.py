import os
import json

all_names = []

for fname in sorted(os.listdir("data")):
    if fname.startswith("names-"):
        with open("data/{fname}".format(fname=fname)) as f:
            names = json.load(f)
            all_names.extend(names)

print(len(all_names))
with open("data/all-names.json", "w") as f:
    json.dump(all_names, f, indent=4)