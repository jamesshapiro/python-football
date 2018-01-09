#!/usr/bin/env python3 -tt

import requests
import re
import collections
import json
from unidecode import unidecode
import bs4
import sys
import maya

ACC = ['Boston College', 'Clemson', 'Florida State', 'Louisville', 'North Carolina State', 'NC State', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'Miami', 'Miami (FL)', 'North Carolina', 'Pittsburgh', 'Virginia', 'Virginia Tech']
BIG_12 = ['Baylor', 'Iowa State', 'Kansas', 'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas', 'Texas Tech', 'West Virginia']
BIG_TEN = ['Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State', 'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin']
PAC_12 = ['Arizona', 'Arizona State', 'California', 'UCLA', 'Colorado', 'Oregon', 'Oregon State', 'USC', 'Stanford', 'Utah', 'Washington', 'Washington State']
SEC = ['Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Mississippi', 'Ole Miss', 'Mississippi State', 'Missouri', 'South Carolina', 'Tennessee', 'Texas A&M', 'Texas A&amp;M', 'Vanderbilt']

POWER_5 = ACC + BIG_12 + BIG_TEN + PAC_12 + SEC

only_tally_first_rounders = False
last_five_years = True
CURRENT_YEAR = maya.now().datetime().year
SINCE_BCS = 1999
LAST_FIVE_YEARS = CURRENT_YEAR - 5
LAST_TEN_YEARS = CURRENT_YEAR - 10
url_template = 'https://en.wikipedia.org/wiki/{}_NFL_Draft'

years = [url_template.format(year) for year in range(SINCE_BCS, CURRENT_YEAR)]
if last_five_years:
    years = [url_template.format(year) for year in range(LAST_FIVE_YEARS, CURRENT_YEAR)]

def is_draft_pick_row(row):
    return '<span id="Pick_' in str(row)

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
    

def tally_drafts(urls):
    schools = []
    for url in urls:
        print('downloading... ' + url)
        draft_picks_raw_html = unidecode(requests.get(url).text)
        soup = bs4.BeautifulSoup(draft_picks_raw_html, "html.parser")
        tag = 'tr'
        tags = soup.find_all(tag)
        tags = list(filter(is_draft_pick_row, tags))
        for t in tags:
            l = [child for child in t.children if child != u'\n']
            result = list(re.split(r'[<>]', str(l[1])))
            draft_round = result[len(result) // 2]
            if only_tally_first_rounders and draft_round != "1":
                continue
            try:
                school = re.split(r'[<>]', str(l[6]))[4]
                if school in POWER_5:
                    schools.append(school)
            except IndexError:
                pass
        
    conferences = map(school_to_conference, schools)
    c = collections.Counter(conferences)
    total = len(conferences)
    for school in c:
        percent = format(100 * c[school] / total, '.1f')
        result = '{}: {}% ({}/{})'.format(school, percent, c[school], total)
        print(result)
    
tally_drafts(years)
