#!/usr/local/bin/python

################################################################################
# IMPORTS                                                                      #
################################################################################

import MySQLdb
import bbparser
import urllib

################################################################################
# DECLARATIONS                                                                 #
################################################################################

connection = MySQLdb.connect(host='localhost', user='whweaver_bbupdat', passwd='3m;*h,[Uke}e', db='whweaver_broomball', charset='utf8')
cursor = connection.cursor()

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
		print('\t\tLeague ' + str(name))
		self.cursor.callproc('add_league_url', (url, name, self.year))
		leagid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return leagid
		
	def foundConference(self, url, name, leagid):
		print('\t\t\tConference ' + str(name))
		self.cursor.callproc('add_conference_url', (url, name, leagid))
		confid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return confid
		
	def foundTeam(self, leagid, confid, urlnum, name, wins, losses, ties, otlosses, gf, ga):
		pass
		return None

################################################################################
# MAIN                                                                         #
################################################################################

cursor.callproc('get_years')
for result in cursor.fetchall():
	while cursor.nextset() is not None: pass
	print('Parsing season pages')
	sp = TeamListStorage(result[0], cursor)
	season = urllib.urlopen('http://www.broomball.mtu.edu/teams/view/' + str(result[0])).read().decode('utf8')
	sp.feed(season)
		
connection.commit()
cursor.close()
connection.close()

################################################################################
# EOF                                                                          #
################################################################################