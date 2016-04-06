#!/usr/local/bin/python

################################################################################
# IMPORTS                                                                      #
################################################################################

import bbparser
import urllib

################################################################################
# CLASSES                                                                      #
################################################################################

class TeamListStorage(bbparser.SeasonParser):
	cursor = None
	year = None

	def __init__(self, year, cursor):
		bbparser.SeasonParser.__init__(self)
	
		self.cursor = cursor
		self.year = year

	def foundLeague(self, url, name):
		print((url, name))
		return url;
		
	def foundConference(self, url, name, leagid):
		print((url, name, leagid))
		return url;
		
	def foundTeam(self, leagid, confid, urlnum, name, wins, losses, ties, otlosses, gf, ga):
		print((leagid, confid, urlnum, name, wins, losses, ties, otlosses, gf, ga))

################################################################################
# MAIN                                                                         #
################################################################################

sp = TeamListStorage(2016, None)
season2016 = urllib.urlopen('http://www.broomball.mtu.edu/teams/view/').read().decode('utf8')
sp.feed(season2016)

################################################################################
# END OF FILE                                                                  #
################################################################################
