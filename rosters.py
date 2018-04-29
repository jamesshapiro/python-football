#!/usr/bin/env python3 -tt

import pandas as pd
import collections
#import boto3
#import s3transfer
import sys
#from botocore.client import Config

def nameToPlayer(lastfirst):
    if type(lastfirst) == str:
        if len(lastfirst.split(', ')) == 2:
            last, first = lastfirst.split(', ')
            return '{} {}'.format(first, last)
    print(lastfirst)
    return lastfirst

def heightToInches(height):
    if type(height) == str:
        height = height.replace('"','').replace("'",'-').split('-')
        inches = 0
        feet = int(height[0])
        if len(height) == 2:
            inches = int(height[1])
        return feet * 12 + inches
    return height

def lambda_handler(event, context):
    team_urls = [('Redskins', 'http://www.redskins.com/team/roster.html', 0),
         ('Broncos', 'http://www.denverbroncos.com/team/roster.html', 0),
         ('Chiefs', 'http://www.chiefs.com/team/roster.html', 0),
         ('Chargers', 'http://www.chargers.com/team/roster', 0),
         ('Raiders', 'http://www.raiders.com/team/roster.html', 0),
         ('Texans', 'http://www.houstontexans.com/team/roster.html', 0),
         ('Colts', 'http://www.colts.com/team/roster.html', 0),
         ('Jaguars', 'http://www.jaguars.com/team/roster.html', 2),
         ('Titans', 'http://www.titansonline.com/team/roster.html', 0),
         ('Ravens', 'http://www.baltimoreravens.com/team/roster.html', 0),
         ('Bengals', 'http://www.bengals.com/team/roster.html', 0),
         ('Browns', 'http://www.clevelandbrowns.com/team/roster.html', 0),
         ('Steelers', 'http://www.steelers.com/team/roster.html', 0),
         ('Bills', 'http://www.buffalobills.com/team/roster.html', 0),
         ('Dolphins', 'http://www.miamidolphins.com/team/player-roster.html', 0),
         ('Patriots', 'http://www.patriots.com/team/roster', 0),
         ('Jets', 'http://www.newyorkjets.com/team/roster.html', 0),
         ('Cowboys', 'http://www.dallascowboys.com/team/roster.html', 0),
         ('Eagles', 'http://www.philadelphiaeagles.com/team/roster.html', 0),
         ('Giants', 'http://www.giants.com/team/roster.html', 0),
         ('Bears', 'http://www.chicagobears.com/team/roster.html', 0),
         ('Lions', 'http://www.detroitlions.com/team/roster.html', 1),
         ('Packers', 'http://www.packers.com/team/players.html', 0),
         ('Vikings', 'http://www.vikings.com/team/roster.html', 0),
         ('Falcons', 'http://www.atlantafalcons.com/team/player-roster.html', 0),
         ('Panthers', 'http://www.panthers.com/team/roster.html', 0),
         ('Saints', 'http://www.neworleanssaints.com/team/roster.html', 0),
         ('Buccaneers', 'http://www.buccaneers.com/team-and-stats/roster.html', 0),
         ('Cardinals', 'http://www.azcardinals.com/roster/player-roster.html', 0),
         ('Rams', 'http://www.therams.com/team/roster.html', 0),
         ('49ers', 'http://www.49ers.com/team/roster.html', 0),
         ('Seahawks', 'http://www.seahawks.com/team/roster', 0)]
    rosters = collections.defaultdict(lambda: list())

    dfs = []
    for team, url, table_index in team_urls:
        print('loading {}...'.format(team))
        data = pd.read_html(url)[table_index]
        cols = list(map(lambda column: ''.join(column.split()), data.columns.values))
        cols = list(map(lambda column: column.replace('.','').capitalize(), cols))
        data.columns = cols
        if 'Name' in cols:
            data['Player'] = data['Name'].apply(nameToPlayer)
            data = data.drop(['Name'], axis=1)
        data['Team'] = data['Age'].apply(lambda x: team)
        data['HtInches'] = data['Ht'].apply(heightToInches)
        dfs.append(data)
    
    rosters = pd.concat(dfs, ignore_index=True)
    # S3 Connect
    """
    client = boto3.client('s3')
    g = open('/tmp/rosters.json', 'w')
    g.write(json.dumps(rosters))
    g.close()
    """
    
    """    with open('/tmp/rosters.json', 'rb') as f:
        client.upload_fileobj(f, 'nflrosters', 'rosters.json', ExtraArgs={'ACL': 'public-read'})
    """        
    return rosters

my_rosters = lambda_handler(None, None)
print('Top 20 schools by number of NFL players currently on a roster:')
print(my_rosters['College'].value_counts().head(10))
print(my_rosters.head(10))

print('The heaviest player in the NFL')
print(my_rosters.iloc(0)[my_rosters['Wt'].idxmax()])

print('The tallest players in the draft')
print(my_rosters[my_rosters['HtInches'] == my_rosters['HtInches'].max()])
