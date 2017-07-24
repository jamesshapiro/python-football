#!/usr/bin/env python3 -tt

import requests
import re
import collections

playerRegex = '<a href="/team/roster/[\w\-]+/[a-f\d\-]+" rel="/cda-web/person-card-module.htm\?mode=data&id=[a-f\d\-]+" rev="Player" class="player-card-tooltip" title="([a-zA-Z]+, [a-zA-Z]+)"><span>[a-zA-Z]+, [a-zA-Z]+</span></a>'

links = [("Redskins", "http://www.redskins.com/team/roster.html"),
         ("Saints", "http://www.neworleanssaints.com/team/roster.html"),
         ("Broncos", "http://www.denverbroncos.com/team/roster.html"),
         ("Chiefs", "http://www.chiefs.com/team/roster.html"),
         ("Chargers", "http://www.chargers.com/team/roster"),
         ("Raiders", "http://www.raiders.com/team/roster.html"),
         ("Texans", "http://www.houstontexans.com/team/roster.html"),
         ("Colts", "http://www.colts.com/team/roster.html"),
         ("Jaguars", "http://www.jaguars.com/team/roster.html"),
         ("Titans", "http://www.titansonline.com/team/roster.html"),
         ("Ravens", "http://www.baltimoreravens.com/team/roster.html"),
         ("Bengals", "http://www.bengals.com/team/roster.html"),
         ("Browns", "http://www.clevelandbrowns.com/team/roster.html"),
         ("Steelers", "http://www.steelers.com/team/roster.html"),
         ("Bills", "http://www.buffalobills.com/team/roster.html"),
         ("Dolphins", "http://www.miamidolphins.com/team/player-roster.html"),
         ("Patriots", "http://www.patriots.com/team/roster"),
         ("Jets", "http://www.newyorkjets.com/team/roster.html")
]

qbs = {"Redskins": "Kirk Cousins",
       "Saints": "Drew Brees",
       "Broncos": "Trevor Siemian",
       "Chiefs": "Alex Smith",
       "Chargers": "Philip Rivers",
       "Raiders": "Derek Carr",
       "Texans": "Deshaun Watson",
       "Colts": "Andrew Luck",
       "Jaguars": "Blake Bortles",
       "Titans": "Marcus Mariota",
       "Ravens": "Joe Flacco",
       "Bengals": "Andy Dalton",
       "Browns": "Brock Osweiler",
       "Steelers": "Ben Roethlisberger",
       "Bills": "Tyrod Taylor",
       "Dolphins": "Ryan Tannehill",
       "Patriots": "Tom Brady",
       "Jets": "Josh McCown"}

rosters = collections.defaultdict(lambda: list())

for (team, url) in links:
    rosterRawHtml = requests.get(url).text
    #print(rosterRawHtml)
    p = re.compile(playerRegex)
    matches = p.finditer(rosterRawHtml)
    for match in matches:
        [last, first] = match.group(1).split(", ")
        rosters[team].append("{} {}".format(first, last))

for roster in rosters:
    if qbs[roster] not in rosters[roster]:
        print("WARNING: {} not found on {}'s roster".format(qbs[roster], roster))
    else:
        print("OK: {} is on {}'s roster".format(qbs[roster], roster))
    print(len(rosters[roster]))


