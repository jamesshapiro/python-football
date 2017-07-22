#!/usr/bin/env python3 -tt

import requests
import re
import collections

playerRegex = '<a href="/team/roster/[\w\-]+/[a-f\d\-]+" rel="/cda-web/person-card-module.htm\?mode=data&id=[a-f\d\-]+" rev="Player" class="player-card-tooltip" title="([a-zA-Z]+, [a-zA-Z]+)"><span>[a-zA-Z]+, [a-zA-Z]+</span></a>'

links = [("Redskins", "http://www.redskins.com/team/roster.html"), ("Saints", "http://www.neworleanssaints.com/team/roster.html")]
regexes = {"Redskins": '<a href="/team/roster/[\w\-]+/[a-f\d\-]+" rel="/cda-web/person-card-module.htm\?mode=data&id=[a-f\d\-]+" rev="Player" class="player-card-tooltip" title="([a-zA-Z]+, [a-zA-Z]+)"><span>[a-zA-Z]+, [a-zA-Z]+</span></a>', "Saints" : '<a href="/team/roster/[\w\-]+/[a-f\d\-]+" rel="/cda-web/person-card-module.htm\?mode=data&id=[a-f\d\-]+" rev="Player" class="player-card-tooltip" title="([a-zA-Z]+, [a-zA-Z]+)"><span>[a-zA-Z]+, [a-zA-Z]+</span></a>'}

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
    for name in rosters[roster]:
        print(name)
    print(len(rosters[roster]))


