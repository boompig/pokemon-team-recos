'''
Because it's only one post this doesn't have to be very fancy
'''

from bs4 import BeautifulSoup
from pprint import pprint
from typing import Optional
from html2text import html2text
import os
import json


def parse_comment_soup(comment: BeautifulSoup):
    # get metadata
    # mainly we care about the votes
    net_vote_count = int(comment.find('span', {'class': 'qa-netvote-count-data'}).text)

    # here we get the content
    content_soup = comment.find(
        'div',
        {'class': 'qa-a-item-content'}
    ).find(
        'div',
        {'itemprop': 'text'}
    )

    return {
        'net_vote_count': net_vote_count,
        'content_text': html2text(content_soup.prettify()),
        'content_original_markup': content_soup.prettify(),
    }


def parse_question_soup(soup: BeautifulSoup):
    # get metadata
    # mainly we care about the votes
    net_vote_count = int(soup.find('span', {'class': 'qa-netvote-count-data'}).text)

    # here we get the content
    content_soup = soup.find(
        'div',
        {'class': 'qa-q-view-main'}
    ).find(
        'div',
        {'itemprop': 'text'}
    )

    return {
        'net_vote_count': net_vote_count,
        'content_text': html2text(content_soup.prettify()),
        'content_original_markup': content_soup.prettify(),
    }




def extract_content(soup: BeautifulSoup):
    # find the content
    main = soup.find('div', {'class': 'qa-body-wrapper'})  # type: BeautifulSoup
    # remove some non-content divs
    main.find('div', {'class': 'qa-sidepanel'}).decompose()
    for form in main.findAll('div', {'class': 'qa-c-form'}):
        form.decompose()
    main.find('div', {'class': 'qa-page-links'}).decompose()

    results = {
        'comments': []
    }

    # this is the question
    q_soup = main.find(
        'div',
        {'class': 'qa-q-view'}
    )
    results['question'] = parse_question_soup(q_soup)
    # pprint(q_data['content_text'])

    # these are the comments
    for comment in main.findAll('div', {'class': 'qa-a-list-item'}):
        results['comments'].append(parse_comment_soup(comment))
    return results


def parse(fname: str):
    with open(fname) as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
    return extract_content(soup)


def save(out_dir: str, results: dict):
    fname = os.path.join(out_dir, 'parsed.json')
    with open(fname, 'w') as f:
        json.dump(results, f, sort_keys=True, indent=4)
    return fname


if __name__ == '__main__':
    # fname = './data/pokemondb-post/raw/What is a good in-game team for Omega Ruby and Alpha Sapphire  - PokéBase Pokémon Answers.html'
    dir = './data/pokemondb-post/raw'
    out_dir = './data/pokemondb-post/parsed'
    page = 1
    results = {'comments': []}
    for fname in sorted(os.listdir(dir)):
        if fname.endswith('.html'):
            path = os.path.join(dir, fname)
            print('Parsing %s...' % path)
            page_r = parse(path)
            if page == 1:
                results['question'] = page_r['question']
            results['comments'].extend(page_r['comments'])
            page += 1
    out_fname = save(out_dir, results)
    print('Wrote to %s' % out_fname)