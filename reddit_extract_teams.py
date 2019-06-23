"""
I am using a context-less parsing
"""

import praw
import json
from typing import List, Set
import string
import logging
from Levenshtein import distance
import os

username = "rrrriddikulus"
password = "FEcVc3.oC7+i7k6s"

client_id = "y_9kOsOlZECgDQ"
secret = "b32pVQ6HRSStHO_JDkvL5Jf7h9M"
script_name = 'pokemon-comment-parser'

version = '0.0.1'
platform = 'ubuntu'

user_agent = '{platform}:${app_id}:${version} (by /u/${username})'.format(
    platform=platform,
    app_id=client_id,
    version=version,
    username=username,
)


def save_post_and_comments(submission, url: str, fname: str) -> None:
    results = {}
    results["url"] = url
    results["selftext"] = submission.selftext
    results["comments"] = []
    for top_level_comment in submission.comments:
        results["comments"].append(top_level_comment.body)
    with open(fname, "w") as f:
        json.dump(results, f, indent=4)


def extract_tokens_from_post(post: str) -> List[str]:
    """Tokens are normalized and made lowercase"""
    table = str.maketrans({
        "/": " ",
        ".": " ",
        ",": " ",
        "!": " ",
        ")": " ",
        "(": " ",
        ":": " ",
        "\n": " ",
    })
    parts = post.translate(table).split(" ")
    def normalize_token(token):
        # token already lowercase
        if token == "pika":
            return "pikachu"
        elif "rotom" in token:
            return "rotom"
        else:
            return token
    # extract tokens
    clean_tokens = [normalize_token(part.lower()) for part in parts if part]
    return clean_tokens


def extract_team_definite(clean_tokens: List[str], pokemon_list: Set[str]) -> List[str]:
    """
    I previously queried the pokemon API to extract the names of pokemon
    Returned pokemon names are all lower case
    """
    # then just filter by pokemon_list
    team = [token for token in clean_tokens if token in pokemon_list]
    return team


def extract_team_possible(clean_tokens: List[str], words: Set[str]) -> List[str]:
    """
    Use the words method to extra pokemon
    Returned pokemon names are all lower case
    """
    def is_pokemon(token: str):
        if token == "porygon-z":
            return True
        # tokens are all lower-case
        return token not in words and token.isalpha()

    team = [token for token in clean_tokens if is_pokemon(token)]
    return team


def read_words() -> Set[str]:
    words = set([])
    with open("/usr/share/dict/american-english") as f:
        for line in f:
            words.add(line.rstrip().lower())
    # add a few internet words
    words.add("lol")
    words.add("alot")
    words.add("aka") # AKA
    words.add("haha")
    # a few common words
    words.add("storyline")
    words.add("monotype")
    # add some pokemon terminology that's likely to come up
    words.add("hm")
    words.add("hms")
    words.add("oras")
    words.add("mega")
    words.add("pokemon")
    words.add("dex")
    words.add("exp")
    words.add("supereffective")
    words.add("dexnav")
    words.add("hoenn")
    words.add("asapphire")
    words.add("oruby")
    words.add("libre")
    # cosplay pikachu
    words.add("cosplay")
    words.add("unevolved")
    words.add("megastone")
    # words that are also pokemon
    words.remove("slaking")
    words.remove("electrode")
    words.remove("aron")
    return words


def read_pokemon_list() -> Set[str]:
    """
    Pokemon all in lower case
    """
    mons = []
    with open("data/clean-names.json") as f:
        mons.extend(json.load(f))
    return set([pk.lower() for pk in mons])


def extract_team(possible: Set[str], definite: Set[str], pokemon_list: Set[str]) -> List[str]:
    try:
        assert definite.issubset(possible)
    except AssertionError as e:
        print(definite - possible)
        print(definite)
        print(possible)
        raise e
    # these are the ones we care about
    misspelt_pokemon = possible - definite
    if not misspelt_pokemon:
        return list(definite)

    # find the closest pokemon in terms of edit distance to these pokemon
    edit_table = {}
    for mistake in misspelt_pokemon:
        min_dist = -1
        min_dist_pk = None
        for pokemon in pokemon_list:
            dist = distance(mistake, pokemon)
            if min_dist < 0 or dist < min_dist:
                min_dist = dist
                min_dist_pk = pokemon
        edit_table[mistake] = {
            "mon": min_dist_pk,
            "distance": dist
        }
    team = list(definite)
    if len(team) != 6:
        # add all the ones that are 2 or less
        for k, v in edit_table.items():
            if v["distance"] <= 2:
                logging.info("adding %s to team" % v["mon"])
                team.append(v["mon"])
    else:
        logging.warning("team exactly 6, ignoring possible errors")
    return team


def read_reddit(url, output_dir):
    reddit = praw.Reddit(client_id=client_id,
                        client_secret=secret,
                        user_agent=user_agent)
    assert reddit.read_only
    submission = reddit.submission(url=url)
    fname = os.path.join(output_dir, "oras-{}.json".format(submission.id))
    save_post_and_comments(submission, url, fname)
    return fname


def extract_teams_from_post(post_fname):
    words = read_words()

    pokemon_list = read_pokemon_list()
    print("loaded %d pokemon" % len(pokemon_list))

    comments = []
    with open(post_fname) as f:
        contents = json.load(f)
        comments.append(contents["selftext"])
        for comment in contents["comments"]:
            comments.append(comment)

    teams = []
    for comment in comments:
        clean_tokens = extract_tokens_from_post(comment)
        definite = extract_team_definite(clean_tokens, pokemon_list)
        possible = extract_team_possible(clean_tokens, words)
        team = extract_team(set(possible), set(definite), pokemon_list)
        teams.append(team)
        print(team)
        print("-----")
    return teams


if __name__ == '__main__':
    submission_dir = "data/submissions"
    # url = 'https://www.reddit.com/r/pokemon/comments/3xmb42/your_oras_team/'
    # url = 'https://www.reddit.com/r/pokemon/comments/5tjapu/pokemon_oras_what_was_your_team/'
    # url = 'https://www.reddit.com/r/pokemon/comments/2ns5sg/whats_your_in_game_oras_team/'
    # url = 'https://www.reddit.com/r/pokemon/comments/2fugiw/oras_playthrough_teams/'
    # url = 'https://www.reddit.com/r/pokemon/comments/2n71kc/whats_currently_your_oras_team/'

    # fname = read_reddit(url, submission_dir)
    # print(fname)
    for fname in os.listdir(submission_dir):
        path = os.path.join(submission_dir, fname)
        teams = extract_teams_from_post(path)
        out_path = os.path.join("data/teams", fname)
        with open(out_path, "w") as f:
            json.dump(teams, f, indent=4)
