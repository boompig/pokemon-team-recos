"""
I am using a context-less parsing
"""

import praw
import json
from typing import List, Set, Tuple
import logging
from Levenshtein import distance
import os
from argparse import ArgumentParser

from reddit_secret import username, client_id, secret

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
    results["id"]: submission.id
    results["comments"] = []
    results["comment_ids"] = []
    for top_level_comment in submission.comments:
        results["comments"].append(top_level_comment.body)
        results["comment_ids"].append(top_level_comment.id)
    with open(fname, "w") as f:
        json.dump(results, f, indent=4, sort_keys=True)


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
    fname = "data/dictionary/words_alpha.txt"
    with open(fname) as f:
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
    words.add("playthrough")
    words.add("favourites")
    words.add("jizzed")
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
    words.add('lvl')
    words.add('ev')
    words.add('op')
    words.add('uu')
    words.add('ru')
    words.add('ou')
    # cosplay pikachu
    words.add("cosplay")
    words.add("unevolved")
    words.add("megastone")
    # words that are also pokemon
    words.remove("slaking")
    words.remove("electrode")
    words.discard("aron") # sometimes in word list
    words.discard("skitty") # sometimes in word list
    words.discard("golem") # sometimes in word list
    words.discard("chatot") # sometimes in word list
    return words


def read_pokemon_list() -> Set[str]:
    """
    Pokemon all in lower case
    """
    mons = []
    with open("data/pokemon-names/clean-names.json") as f:
        mons.extend(json.load(f))
    return set([pk.lower() for pk in mons])


def suggest_correction(user_str: str, potentials: Set[str]) -> Tuple[int,str]:
    min_dist = -1
    min_dist_word = None
    for word in potentials:
        dist = distance(user_str, word)
        if min_dist < 0 or dist < min_dist:
            min_dist = dist
            min_dist_word = word
    return min_dist, min_dist_word


def extract_team(possible: Set[str], definite: Set[str], pokemon_list: Set[str], words: Set[str]) -> List[str]:
    try:
        assert definite.issubset(possible)
    except AssertionError as e:
        print("definite - possible:")
        print(definite - possible)
        print("definite:")
        print(definite)
        print("possible:")
        print(possible)
        raise e
    # these are the ones we care about
    misspelt_pokemon = possible - definite
    if not misspelt_pokemon:
        return list(definite)

    # find the closest pokemon in terms of edit distance to these pokemon
    edit_table = {}
    for mistake in misspelt_pokemon:
        mon_dist, min_dist_pk = suggest_correction(mistake, pokemon_list)
        word_dist, min_word = suggest_correction(mistake, words)
        edit_table[mistake] = {
            "mon": min_dist_pk,
            "mon_distance": mon_dist,
            "word": min_word,
            "word_distance": word_dist
        }
    team = list(definite)
    if len(team) != 6:
        # add all the ones that are 2 or less
        for k, v in edit_table.items():
            if v["mon_distance"] <= 2:
                logging.info("adding %s to team" % v["mon"])
                team.append(v["mon"])
    else:
        logging.warning("team exactly 6, ignoring possible errors")
        for k, v in edit_table.items():
            logging.debug("misspellings: %s -> %s (%d) or -> %s (%d)", k, v["mon"], v["mon_distance"], v["word"], v["word_distance"])
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


def extract_teams_generic(corpora: List[str]) -> list:
    words = read_words()
    pokemon_list = read_pokemon_list()
    logging.debug("loaded %d pokemon" % len(pokemon_list))

    n = 0
    for pk in pokemon_list:
        if pk in words:
            n += 1
            words.remove(pk)
    logging.info('Removed %d pokemon from english word list', n)

    teams = []
    for corpus in corpora:
        clean_tokens = extract_tokens_from_post(corpus)
        definite = extract_team_definite(clean_tokens, pokemon_list)
        possible = extract_team_possible(clean_tokens, words)
        team = extract_team(set(possible), set(definite), pokemon_list, words)
        teams.append(team)
    print("Read %d teams" % len(teams))
    print("-----")
    return teams


def extract_teams_reddit(post_fname: str):
    comments = []
    with open(post_fname) as f:
        contents = json.load(f)
        print("Parsing submission ID %s..." % contents["id"])
        comments.append(contents["selftext"])
        for comment in contents["comments"]:
            comments.append(comment)
    return extract_teams_generic(comments)


def extract_teams_html(fname: str):
    corpora = []
    with open(fname) as f:
        contents = json.load(f)
        # NOTE: question should actually be blank for PokemonDB
        corpora.append(contents['question']['content_text'])
        for comment in contents['question_comments']:
            corpora.append(comment['content_text'])
        for answer in contents['answers']:
            corpora.append(answer['content_text'])
    return extract_teams_generic(corpora)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-m', '--method', choices=['reddit', 'html'], default='reddit',
                        help='Data format of the input file')
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument('-f', '--file', help='read data from file')
    g.add_argument('-d', '--dir', help='read data from directory')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    extract_fn = (extract_teams_reddit if args.method == 'reddit' else extract_teams_html)

    if args.dir:
        for fname in os.listdir(args.dir):
            path = os.path.join(args.dir, fname)
            teams = extract_fn(path)
            out_path = os.path.join("data/teams", fname)
            with open(out_path, "w") as f:
                json.dump(teams, f, indent=4, sort_keys=True)
    else:
        teams = extract_fn(args.file)
        base = os.path.basename(args.file)
        out_path = os.path.join("data/teams", base)
        with open(out_path, "w") as f:
            json.dump(teams, f, indent=4, sort_keys=True)
        print('Wrote to %s' % out_path)

