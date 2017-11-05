#!/usr/bin/env python3 -tt

import requests
import re
import collections
import json
import boto3
import s3transfer
from botocore.client import Config
from unidecode import unidecode
import bs4

print('Hail to the Redskins!')

def lambda_handler(event, context):
    default_player_tags = ['a', { "class" : "player-card-tooltip" }]
    default_jersey_tags = ['td', { "class" : "col-jersey" }]
    defaults = [default_player_tags, default_jersey_tags]
    chargers_player_tags = ['a', { "class" : "player" }]
    chargers_jersey_tags = ['div', { "class": "field field--name-field-jersey-number field--type-number-integer field--label-hidden" } ]
    chargers_defaults = [chargers_player_tags, chargers_jersey_tags]
    
    team_urls = [("Redskins", "http://www.redskins.com/team/roster.html", defaults),
         ("Broncos", "http://www.denverbroncos.com/team/roster.html", defaults),
         ("Chiefs", "http://www.chiefs.com/team/roster.html", defaults),
         ("Chargers", "http://www.chargers.com/team/roster", chargers_defaults),
         ("Raiders", "http://www.raiders.com/team/roster.html", defaults),
         ("Texans", "http://www.houstontexans.com/team/roster.html", defaults),
         ("Colts", "http://www.colts.com/team/roster.html", defaults),
         ("Jaguars", "http://www.jaguars.com/team/roster.html", defaults),
         ("Titans", "http://www.titansonline.com/team/roster.html", defaults),
         ("Ravens", "http://www.baltimoreravens.com/team/roster.html", defaults),
         ("Bengals", "http://www.bengals.com/team/roster.html", defaults),
         ("Browns", "http://www.clevelandbrowns.com/team/roster.html", defaults),
         ("Steelers", "http://www.steelers.com/team/roster.html", defaults),
         ("Bills", "http://www.buffalobills.com/team/roster.html", defaults),
         ("Dolphins", "http://www.miamidolphins.com/team/player-roster.html", defaults),
         ("Patriots", "http://www.patriots.com/team/roster", chargers_defaults),
         ("Jets", "http://www.newyorkjets.com/team/roster.html", defaults),
         ("Cowboys", "http://www.dallascowboys.com/team/roster.html", chargers_defaults),
         ("Eagles", "http://www.philadelphiaeagles.com/team/roster.html", defaults),
         ("Giants", "http://www.giants.com/team/roster.html", defaults),
         ("Bears", "http://www.chicagobears.com/team/roster.html", defaults),
         ("Lions", "http://www.detroitlions.com/team/roster.html", defaults),
         ("Packers", "http://www.packers.com/team/players.html", defaults),
         ("Vikings", "http://www.vikings.com/team/roster.html", defaults),
         ("Falcons", "http://www.atlantafalcons.com/team/player-roster.html", defaults),
         ("Panthers", "http://www.panthers.com/team/roster.html", defaults),
         ("Saints", "http://www.neworleanssaints.com/team/roster.html", defaults),
         ("Buccaneers", "http://www.buccaneers.com/team-and-stats/roster.html", defaults),
         ("Cardinals", "http://www.azcardinals.com/roster/player-roster.html", defaults),
         ("Rams", "http://www.therams.com/team/roster.html", defaults),
         ("49ers", "http://www.49ers.com/team/roster.html", defaults),
         ("Seahawks", "http://www.seahawks.com/team/roster", chargers_defaults)]
    rosters = collections.defaultdict(lambda: list())
    for team, url, tags in team_urls:
        roster_raw_html = unidecode(requests.get(url).text)
        soup = bs4.BeautifulSoup(roster_raw_html, "html.parser")
        player_tags = soup.find_all(*tags[0])
        jersey_tags = soup.find_all(*tags[1])
        if tags == defaults:
            names = [' '.join(player['title'].split(', ')[::-1]) for player in player_tags]
            jerseys = [number.get_text().strip() for number in jersey_tags]
        elif tags == chargers_defaults:
            names = [' '.join(player.get_text().split(', ')[::-1]) for player in player_tags]
            jerseys = [number.get_text().strip() for number in jersey_tags]
        j = 0
        if team == "Patriots":
            j += 6
        for i in range(j, j+53):
            rosters[team].append((names[i], jerseys[i]))
    # S3 Connect
    client = boto3.client('s3')
    g = open('/tmp/rosters.json', 'w')
    g.write(json.dumps(rosters))
    g.close()
    
    with open('/tmp/rosters.json', 'rb') as f:
        client.upload_fileobj(f, 'nflrosters', 'rosters.json', ExtraArgs={'ACL': 'public-read'})
        
    print([(team, len(rosters[team])) for team in rosters.keys()])
    return rosters
