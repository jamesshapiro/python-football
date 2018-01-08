#!/usr/bin/env python3 -tt

import requests
import re
import collections
import json
from unidecode import unidecode
import bs4
import sys

ACC = ['Boston College', 'Clemson', 'Florida State', 'Louisville', 'North Carolina State', 'NC State', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'Miami', 'Miami (FL)', 'North Carolina', 'Pittsburgh', 'Virginia', 'Virginia Tech']
Big12 = ['Baylor', 'Iowa State', 'Kansas', 'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas', 'Texas Tech', 'West Virginia']
BigTen = ['Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State', 'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin']
Pac12 = ['Arizona', 'Arizona State', 'California', 'UCLA', 'Colorado', 'Oregon', 'Oregon State', 'USC', 'Stanford', 'Utah', 'Washington', 'Washington State']
SEC = ['Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Mississippi', 'Ole Miss', 'Mississippi State', 'Missouri', 'South Carolina', 'Tennessee', 'Texas A&M', 'Texas A&amp;M', 'Vanderbilt']
all_confs = ACC[:]
all_confs.extend(Big12)
all_confs.extend(BigTen)
all_confs.extend(Pac12)
all_confs.extend(SEC)

only_tally_first_rounders = True
SINCE_BCS = 1999
LAST_FIVE_YEARS = 2013
LAST_TEN_YEARS = 2008
url_template = 'https://en.wikipedia.org/wiki/{}_NFL_Draft'

years = [url_template.format(year) for year in range(2013, 2018)]

def is_draft_pick_row(row):
    return '<span id="Pick_' in str(row)

def tally_drafts(urls):
    school_counts = []
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
            if len(result) == 5:
                draft_round = result[2]
            else:
                draft_round = result[4]
            if only_tally_first_rounders and draft_round != "1":
                continue
            try:
                school = re.split(r'[<>]', str(l[6]))[4]
                if school in all_confs:
                    school_counts.append(school)
            except IndexError:
                pass
    
    c = collections.Counter(school_counts)
    schools_by_count = []
    for school in c:
        schools_by_count.append((school, c[school]))
    conf_counts = []
    for school in schools_by_count:
        school_name = school[0]
        if school_name in ACC:
            school_conf = 'ACC'
        elif school_name in Big12:
            school_conf = 'Big 12'
        elif school_name in BigTen:
            school_conf = 'Big Ten'
        elif school_name in Pac12:
            school_conf = 'Pac 12'
        else:
            school_conf = 'SEC'
        num_draft_picks = school[1]
        conf_counts.extend([school_conf] * num_draft_picks)
    c = collections.Counter(conf_counts)
    total = sum([c['SEC'], c['ACC'], c['Pac-12'], c['Big Ten'], c['Big 12']])
    for school in c:
        percent = format(100 * c[school] / total, '.1f')
        result = '{}: {}% ({}/{})'.format(school, percent, c[school], total)
        print(result)
    
tally_drafts(years)
