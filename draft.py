#!/usr/bin/env python3 -tt

"""Usage:
  draft.py [options]

Options:
  -h --help               show this help message and exit
  --from YEAR             start year [default: 1999]
  --lastxyears NUM_YEARS  compute for last X years [default: -1]
"""

import requests
import re
import collections
import json
from unidecode import unidecode
import bs4
import sys
import maya
import os.path
from docopt import docopt

arguments = docopt(__doc__)

ACC = ['Boston College', 'Clemson', 'Florida State', 'Louisville', 'North Carolina State', 'NC State', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'Miami', 'Miami (FL)', 'North Carolina', 'Pittsburgh', 'Virginia', 'Virginia Tech']
BIG_12 = ['Baylor', 'Iowa State', 'Kansas', 'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas', 'Texas Tech', 'West Virginia']
BIG_TEN = ['Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State', 'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin']
PAC_12 = ['Arizona', 'Arizona State', 'California', 'UCLA', 'Colorado', 'Oregon', 'Oregon State', 'USC', 'Stanford', 'Utah', 'Washington', 'Washington State']
SEC = ['Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Mississippi', 'Ole Miss', 'Mississippi State', 'Missouri', 'South Carolina', 'Tennessee', 'Texas A&M', 'Texas A&amp;M', 'Vanderbilt']

def is_draft_pick_row(row):
    return '<span id="Pick_' in str(row)

def get_html(url, year):
    if not os.path.isfile('./{}'.format(year)):
        print('downloading... ' + url)
        text = unidecode(requests.get(url).text)
        with open('./{}'.format(year), 'w') as f:
            f.write(text)
    else:
        print('reading... ' + url)
        with open('./{}'.format(year), 'r') as f:
            text = f.read()
    return text

def tally_draft_picks(tally, message):
    c = collections.Counter(tally)
    total = len(list(tally))
    print(message)
    for school in c.most_common():
        percent = format(100 * c[school[0]] / total, '.1f')
        result = '{}: {}% ({}/{})'.format(school[0], percent, c[school[0]], total)
        print(result)
    print()

def school_to_conference(school):
    if school in ACC:
        return 'ACC'
    elif school in BIG_12:
        return 'Big 12'
    elif school in BIG_TEN:
        return 'Big Ten'
    elif school in PAC_12:
        return 'Pac 12'
    else:
        return 'SEC'

def tally_drafts(years):
    urls = [url_template.format(year) for year in range(START_YEAR, CURRENT_YEAR)]
    first_round_schools = []
    schools = []
    for url, year in zip(urls, years):
        draft_picks_raw_html = get_html(url, year)
        soup = bs4.BeautifulSoup(draft_picks_raw_html, "html.parser")
        tag = 'tr'
        tags = soup.find_all(tag)
        tags = list(filter(is_draft_pick_row, tags))
        for t in tags:
            l = [child for child in t.children if child != u'\n']
            result = list(re.split(r'[<>]', str(l[1])))
            if len(result) == 5 or result[1] == 'th':
                draft_round = result[2]
            else:
                draft_round = result[4]
            try:
                school = re.split(r'[<>]', str(l[6]))[4]
                if school in POWER_5:
                    schools.append(school)
                    if draft_round == "1":
                        first_round_schools.append(school)
            except IndexError:
                pass
    tally_draft_picks(schools, "ALL POWER-5 PICKS BY SCHOOL SINCE {}".format(START_YEAR))
    tally_draft_picks(first_round_schools, "ALL POWER-5 FIRST ROUND PICKS BY SCHOOL SINCE {}".format(START_YEAR))
    draft_picks_by_conf = list(map(school_to_conference, schools))
    first_rounders = list(map(school_to_conference, first_round_schools))
    tally_draft_picks(draft_picks_by_conf, "ALL POWER-5 PICKS SINCE {}".format(START_YEAR))
    tally_draft_picks(first_rounders, "ALL POWER-5 FIRST ROUND PICKS SINCE {}".format(START_YEAR))

if __name__ == '__main__':
    POWER_5 = ACC + BIG_12 + BIG_TEN + PAC_12 + SEC
    CURRENT_YEAR = maya.now().datetime().year
    url_template = 'https://en.wikipedia.org/wiki/{}_NFL_Draft'
    START_YEAR = int(arguments['--from'])
    if arguments['--lastxyears'] != '-1':
        START_YEAR = CURRENT_YEAR - int(arguments['--lastxyears'])
    years = range(START_YEAR, CURRENT_YEAR)
    tally_drafts(years)
