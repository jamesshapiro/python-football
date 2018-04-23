#!/usr/bin/env python3 -tt

"""Usage:
  draft.py [options]

Options:
  -h --help               show this help message and exit
  --from YEAR             start year [default: 1999]
  --lastxyears NUM_YEARS  compute for last X years [default: -1]
"""

import collections
import sys
import maya
import os.path
from docopt import docopt
import pandas as pd

arguments = docopt(__doc__)

ACC = ['Boston College', 'Clemson', 'Florida State', 'Louisville', 'North Carolina State', 'NC State', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'Miami', 'Miami (FL)', 'North Carolina', 'Pittsburgh', 'Virginia', 'Virginia Tech']
BIG_12 = ['Baylor', 'Iowa State', 'Kansas', 'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas', 'Texas Tech', 'West Virginia']
BIG_TEN = ['Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State', 'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin']
PAC_12 = ['Arizona', 'Arizona State', 'California', 'UCLA', 'Colorado', 'Oregon', 'Oregon State', 'USC', 'Stanford', 'Utah', 'Washington', 'Washington State']
SEC = ['Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Mississippi', 'Ole Miss', 'Mississippi State', 'Missouri', 'South Carolina', 'Tennessee', 'Texas A&M', 'Texas A&amp;M', 'Vanderbilt']
POWER_FIVE_DICT = {'ACC': ACC, 'BIG_12': BIG_12, 'BIG_TEN': BIG_TEN, 'PAC_12': PAC_12, 'SEC': SEC}
SCHOOL_TO_CONF = collections.defaultdict(lambda: 'NOT POWER FIVE')
for (conference, schools) in POWER_FIVE_DICT.items():
    SCHOOL_TO_CONF.update({school: conference for school in schools})
        
def get_data(url, year):
    if not os.path.isfile('./{}'.format(year)):
        print('downloading... ' + url)
        data = pd.read_html(url,header=0)
        index = get_index_of_target_table(data)
        players = data[index]
        players.to_csv('./{}'.format(year))
    print('reading... ' + url)
    players = pd.read_csv('./{}'.format(year))
    return players

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
    return SCHOOL_TO_CONF[school]
    
def get_index_of_target_table(data):
    for table_index in range(len(data)):
        players = data[table_index]
        if 'Player' in players.columns:
            return table_index
    print("NO PLAYER TABLE")
    sys.exit(1)

def tally_drafts(years):
    urls = [url_template.format(year) for year in range(START_YEAR, CURRENT_YEAR)]
    all_first_rounders = []
    all_rounders = []
    for (url,year) in zip(urls,years):
        players = get_data(url, year)
        players['Name'] = players['Player'].apply(lambda x: x[len(x)//2 + 1:])
        first_rounders = players[players['Rnd.'] == '1']
        all_first_rounders.extend(list(first_rounders['College']))
        all_rounders.extend(list(players['College']))
    tally_draft_picks(all_rounders, "ALL PICKS BY SCHOOL SINCE {}".format(START_YEAR))
    tally_draft_picks(all_first_rounders, "ALL FIRST ROUND PICKS BY SCHOOL SINCE {}".format(START_YEAR))
    draft_picks_by_conf = list(map(school_to_conference, all_rounders))
    all_first_rounders = list(map(school_to_conference, all_first_rounders))
    tally_draft_picks(draft_picks_by_conf, "ALL PICKS SINCE {}".format(START_YEAR))
    tally_draft_picks(all_first_rounders, "ALL FIRST ROUND PICKS SINCE {}".format(START_YEAR))
        
if __name__ == '__main__':
    POWER_5 = ACC + BIG_12 + BIG_TEN + PAC_12 + SEC
    CURRENT_YEAR = maya.now().datetime().year
    url_template = 'https://en.wikipedia.org/wiki/{}_NFL_Draft'
    START_YEAR = int(arguments['--from'])
    if arguments['--lastxyears'] != '-1':
        START_YEAR = CURRENT_YEAR - int(arguments['--lastxyears'])
    years = range(START_YEAR, CURRENT_YEAR)
    tally_drafts(years)
