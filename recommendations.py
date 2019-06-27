from typing import Dict, List
import json
from pprint import pprint
from collections import Counter
from argparse import ArgumentParser

def read_teams() -> Dict[str, list]:
    teams = {}
    with open('data/teams/all-reddit-teams.json') as f:
        teams['reddit'] = json.load(f)
    with open('data/teams/pokemondb-222207.json') as f:
        teams['pokemondb'] = json.load(f)
    return teams


def get_evolutions(mon: str) -> List[str]:
    mon = mon.lower()
    if mon == 'treecko':
        return ['treecko', 'grovyle', 'sceptile']
    elif mon == 'torchic':
        return ['torchic', 'combusken', 'blaziken']
    else:
        raise Exception('not implemented for %s' % mon)

# start with a source pokemon
# recommend a team that goes well with that pokemon

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-s', '--sources', choices=['reddit', 'pokemondb', 'all'], default='all')
    parser.add_argument('-n', '--count', default=30, type=int)
    parser.add_argument('--starter', default='Treecko')
    args = parser.parse_args()

    if args.sources == 'all':
        ok_sources = [
            'reddit',
            'pokemondb'
        ]
    else:
        ok_sources = [args.sources]

    search_list = [mon.lower() for mon in get_evolutions(args.starter)]

    # already lower-case
    teams_d = read_teams()
    basket = Counter()

    print('Using source: %s' % args.sources)
    print('Most common pokemon in teams with %s or its evolutions' % args.starter)

    for src, teams in teams_d.items():
        if src in ok_sources:
            for team in teams:
                found = None
                for mon in search_list:
                    if mon in team:
                        # print('found relevant team in {}: {}'.format(src, team))
                        found = mon
                        break
                if found:
                    bag = set(team)
                    bag.discard(found)
                    basket.update(bag)

    pprint(basket.most_common(args.count))
