'''
Because it's only one post this doesn't have to be very fancy
'''

from bs4 import BeautifulSoup
# from typing import Optional
from html2text import html2text
import os
import json


def parse_answer_soup(comment: BeautifulSoup):
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


def parse_question_comment_soup(soup: BeautifulSoup):
    # net_vote_count = int(soup.find('span', {'class': 'qa-netvote-count-data'}).text)
    content_soup = soup.find(
        'div',
        {'class': 'qa-c-item-content'}
    ).find(
        'div',
        {'itemprop': 'text'}
    )
    return {
        # 'net_vote_count': net_vote_count,
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
        'question_comments': [],
        'answers': []
    }

    # this is the question
    q_soup = main.find(
        'div',
        {'class': 'qa-q-view'}
    )
    results['question'] = parse_question_soup(q_soup)

    # these are the comments on the question only
    for comment in main.find('div', {'class': 'qa-q-view-c-list'}).findAll('div', {'class': 'qa-c-list-item'}):
        results['question_comments'].append(parse_question_comment_soup(comment))

    # these are the answers
    for answer in main.findAll('div', {'class': 'qa-a-list-item'}):
        results['answers'].append(parse_answer_soup(answer))
    return results


def parse(fname: str):
    with open(fname) as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
    return extract_content(soup)


def save(out_fname: str, results: dict):
    with open(out_fname, 'w') as f:
        json.dump(results, f, sort_keys=True, indent=4)


if __name__ == '__main__':
    dir = './data/pokemondb-post/raw'
    q_id = '222207'
    out_fname = './data/pokemondb-post/parsed/pokemondb-{}.json'.format(q_id)
    page = 1
    results = {
        'question_comments': [],
        'answers': [],
    }
    for fname in sorted(os.listdir(dir)):
        if fname.endswith('.html'):
            path = os.path.join(dir, fname)
            print('Parsing %s...' % path)
            page_r = parse(path)
            if page == 1:
                results['question'] = page_r['question']
            results['question_comments'].extend(page_r['question_comments'])
            results['answers'].extend(page_r['answers'])
            page += 1
    save(out_fname, results)
    print('Wrote to %s' % out_fname)