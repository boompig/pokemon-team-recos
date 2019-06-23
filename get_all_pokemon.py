import requests
import json
import logging
from argparse import ArgumentParser
from pprint import pprint


url = "https://pokeapi.co/api/v2/pokemon/"
species_url = "https://pokeapi.co/api/v2/pokemon-species/"


def get_with_id(i: int, verbose=False):
    r = requests.get(url + str(i))
    if r.status_code != 200:
        raise RuntimeError("Failed to get pokemon with ID %d" % i)
    j = r.json()
    name = j["name"]
    if verbose:
        pprint(j)
    return name


def get_all(min_number: int, max_number: int, verbose=False):
    """
    Arguments are inclusive
    """
    names = []
    last_number = None
    try:
        for i in range(min_number, max_number + 1):
            try:
                print(i)
                name = get_with_id(i, verbose=verbose)
                names.append(name)
                last_number = i
            except RuntimeError as e:
                logging.error(e)
                break
    except KeyboardInterrupt:
        logging.warning("Interrupted by user, exiting")
    return (names, last_number)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    parser = ArgumentParser()
    parser.add_argument("min_number", type=int)
    parser.add_argument("--max-number", type=int, required=False, default=809)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    names, last_number = get_all(args.min_number, args.max_number, verbose=args.verbose)

    fname = "data/pokemon-names/names-{}-{}.json".format(
        args.min_number,
        last_number,
    )
    with open(fname, "w") as fp:
        json.dump(names, fp, indent=4)

    print("Last ID read was {}".format(last_number))
    print("Wrote to {}".format(fname))

