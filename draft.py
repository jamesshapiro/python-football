#!/usr/bin/env python3 -tt

"""Usage:
  draft.py [options]

Options:
  -h --help               show this help message and exit
  --from YEAR             start year [default: 1999]
  --lastxyears NUM_YEARS  compute for last X years [default: -1]
"""

import pandas as pd
import collections
import os
import sys

from docopt import docopt

arguments = docopt(__doc__)

YEARS = range(2009,2018)
url_template = 'https://en.wikipedia.org/wiki/{}_NFL_Draft'
START_YEAR = 1999
CURRENT_YEAR = 2018
years = range(START_YEAR, CURRENT_YEAR)
urls = [url_template.format(year) for year in range(START_YEAR, CURRENT_YEAR)]

ACC = ['Boston College', 'Clemson', 'Florida State', 'Louisville', 'North Carolina State', 'NC State', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'Miami', 'Miami (FL)', 'North Carolina', 'Pittsburgh', 'Virginia', 'Virginia Tech']
BIG_12 = ['Baylor', 'Iowa State', 'Kansas', 'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas', 'Texas Tech', 'West Virginia']
BIG_TEN = ['Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State', 'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin']
PAC_12 = ['Arizona', 'Arizona State', 'California', 'UCLA', 'Colorado', 'Oregon', 'Oregon State', 'USC', 'Stanford', 'Utah', 'Washington', 'Washington State']
SEC = ['Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Mississippi', 'Ole Miss', 'Mississippi State', 'Missouri', 'South Carolina', 'Tennessee', 'Texas A&M', 'Texas A&amp;M', 'Vanderbilt']
POWER_FIVE_DICT = {'ACC': ACC, 'BIG 12': BIG_12, 'BIG TEN': BIG_TEN, 'PAC 12': PAC_12, 'SEC': SEC}
SCHOOL_TO_CONF = collections.defaultdict(lambda: 'OTHER')
for (conference, schools) in POWER_FIVE_DICT.items():
    SCHOOL_TO_CONF.update({school: conference for school in schools})
    
def get_index_of_target_table(data):
    for table_index in range(len(data)):
        players = data[table_index]
        if 'Player' in players.columns:
            return table_index
    print("NO PLAYER TABLE")
    sys.exit(1)    
    
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

dfs = []
for (url,year) in zip(urls,years):
    df = get_data(url, year)
    df['Year'] = df['Player'].apply(lambda x: year)
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df.reindex(columns=(['Year'] + list([a for a in df.columns if a != 'Year'])))
    dfs.append(df)
def fix_name(name):
    if not name.replace(',','').replace(' ','').isalpha():
        name = name[:-2]
    return name[len(name)//2 + 1:]

players = pd.concat(dfs)
players['Name'] = players['Player'].apply(fix_name)
players['Power 5'] = players['College'].apply(lambda college: SCHOOL_TO_CONF[college])

def print_result(description, result):
    print(description, '\n', result, '\n\n')

print_result('ALL FIRST ROUND PICKS BY SCHOOL SINCE 1999', players[players['Rnd.'] == '1']['College'].value_counts().head(20))
print_result('ALL PICKS BY SCHOOL SINCE 1999',
             players['College'].value_counts().head(20))
print_result('ALL FIRST ROUND PICKS SINCE 1999',
             players[players['Rnd.'] == '1']['Power 5'].value_counts())
print_result('ALL PICKS SINCE 1999',
             players['Power 5'].value_counts())
print_result('ALL POWER 5 FIRST ROUND PICKS SINCE 1999',
             players[(players['Rnd.'] == '1') & (players['Power 5'] != 'OTHER')]['Power 5'].value_counts())
print_result('ALL POWER 5 PICKS SINCE 1999',
             players[players['Power 5'] != 'OTHER']['Power 5'].value_counts())

