#!/usr/bin/env python3 -tt
import pandas as pd
import collections
import os
import sys
import maya
import matplotlib.pyplot as plt

url_template = 'https://en.wikipedia.org/wiki/{}_NFL_Draft'

# First year of the BCS National Championship Game
START_YEAR = 1999
CURRENT_YEAR = maya.now().datetime().year

# The NFL draft takes place in late April, so this script automatically incorporates
# data from the most recent draft with a few day's delay
if maya.now().datetime().month > 4:
    CURRENT_YEAR += 1

years = range(START_YEAR, CURRENT_YEAR)
urls = [url_template.format(year) for year in range(START_YEAR, CURRENT_YEAR)]

# Note: Conferences include every school in the conference as of 2018, so players who were drafted
# when their college was not part of a conference are nevertheless tallied as draft picks from
# that conference
ACC = ['Boston College', 'Clemson', 'Florida State', 'Louisville', 'North Carolina State', 'NC State', 'Syracuse', 'Wake Forest', 'Duke', 'Georgia Tech', 'Miami', 'Miami (FL)', 'North Carolina', 'Pittsburgh', 'Virginia', 'Virginia Tech']
BIG_12 = ['Baylor', 'Iowa State', 'Kansas', 'Kansas State', 'Oklahoma', 'Oklahoma State', 'TCU', 'Texas', 'Texas Tech', 'West Virginia']
BIG_TEN = ['Illinois', 'Indiana', 'Iowa', 'Maryland', 'Michigan', 'Michigan State', 'Minnesota', 'Nebraska', 'Northwestern', 'Ohio State', 'Penn State', 'Purdue', 'Rutgers', 'Wisconsin']
PAC_12 = ['Arizona', 'Arizona State', 'California', 'UCLA', 'Colorado', 'Oregon', 'Oregon State', 'USC', 'Stanford', 'Utah', 'Washington', 'Washington State']
SEC = ['Alabama', 'Arkansas', 'Auburn', 'Florida', 'Georgia', 'Kentucky', 'LSU', 'Mississippi', 'Ole Miss', 'Mississippi State', 'Missouri', 'South Carolina', 'Tennessee', 'Texas A&M', 'Texas A&amp;M', 'Vanderbilt']
POWER_FIVE_DICT = {'ACC': ACC, 'BIG 12': BIG_12, 'BIG TEN': BIG_TEN, 'PAC 12': PAC_12, 'SEC': SEC}
SCHOOL_TO_CONF = collections.defaultdict(lambda: 'OTHER')
for (conference, schools) in POWER_FIVE_DICT.items():
    SCHOOL_TO_CONF.update({school: conference for school in schools})

# Wikipedia pages contain a number of tables and the number of tables is inconsistent across years.
# This helper function identifies the index of the table that actually contains the draft picks
# for a given year.
def get_index_of_target_table(data):
    for table_index in range(len(data)):
        players = data[table_index]
        if 'Player' in players.columns:
            return table_index
    print("NO PLAYER TABLE")
    sys.exit(1)    

# Loads the data from disk, if possible, to avoid making slow network requests. Even if no files
# are saved, the script should only take about a minute to run.
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

# The player name field is messily extracted as follows: Newton, CamCam Newton.
# Additionally, in some years, players who have made the Pro Bowl have an obelisk
# after their name. This function is a quick-and-dirty method to extract the player's
# full name, regardless of whether or not it has an obelisk next to it.
def fix_name(name):
    if not name.replace(',','').replace(' ','').isalpha():
        name = name[:-2]
    return name[len(name)//2 + 1:]

players = pd.concat(dfs)
players['Name'] = players['Player'].apply(fix_name)
players['Power 5'] = players['College'].apply(lambda college: SCHOOL_TO_CONF[college])

results = []
results.append('ALL FIRST ROUND PICKS BY SCHOOL SINCE 1999:\n' +
               str(players[players['Rnd.'] == '1']['College'].value_counts().head(20)))
results.append('ALL PICKS BY SCHOOL SINCE 1999:\n' +
               str(players['College'].value_counts().head(20)))
results.append('ALL FIRST ROUND PICKS SINCE 1999:\n' +
               str(players[players['Rnd.'] == '1']['Power 5'].value_counts()))
results.append('ALL PICKS SINCE 1999:\n' +
               str(players['Power 5'].value_counts()))
results.append('ALL POWER 5 FIRST ROUND PICKS SINCE 1999:\n' +
               str(players[(players['Rnd.'] == '1') & (players['Power 5'] != 'OTHER')]['Power 5'].value_counts()))
results.append('ALL POWER 5 PICKS SINCE 1999:\n' +
               str(players[players['Power 5'] != 'OTHER']['Power 5'].value_counts()))
print('\n\n\n'.join(results))



labels = list(POWER_FIVE_DICT.keys())
all_sizes = [len(players[players['Power 5'] == school]) for school in labels]
first_rd_sizes = [len(players[(players['Power 5'] == school) & (players['Rnd.'] == '1')]) for school in labels]
explode = (0, 0, 0, 0, 0.1)
fig, axes = plt.subplots(figsize=(6,2.85), dpi = 200, nrows=1, ncols=2)
axes[0].pie(all_sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90)
axes[0].set_title('Share of All Power 5\n Draft Picks (1999-Present)')
axes[1].pie(first_rd_sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=False, startangle=90)
axes[1].set_title('Share of First Round\n Power 5 Draft Picks (1999-Present)')
plt.show()
