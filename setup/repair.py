#!/usr/local/bin/python

################################################################################
# IMPORTS                                                                      #
################################################################################

import MySQLdb
import bbparser
import urllib
import re
import time

################################################################################
# DECLARATIONS                                                                 #
################################################################################

connection = MySQLdb.connect(host='localhost', user='whweaver_bbupdat', passwd='3m;*h,[Uke}e', db='whweaver_broomball', charset='utf8')
cursor = connection.cursor()

################################################################################
# CLASSES                                                                      #
################################################################################
		
class TeamStorage(bbparser.TeamParser):
	cursor = None
	teamid = None
	
	def __init__(self, teamid, cursor):
		bbparser.TeamParser.__init__(self, teamid)
		
		self.cursor = cursor
		self.teamid = teamid
		
	def foundGame(self, opUrlNum, date, location, gf, ga, ha):
		print('\t\tGame against ' + str(opUrlNum))
		if date != None and location != None:
			self.cursor.callproc('insert_game', (self.teamid, opUrlNum, date, location, gf, ga))
			gameid = self.cursor.fetchone()[0]
			while self.cursor.nextset() is not None: pass
		else:
			gameid = None
		
		return gameid
	
	def foundPlayer(self, playerUrlNum, name, goals, assists, points, pim, saves, goalieMins, goalsAgainst):
		pass
		

################################################################################
# MAIN                                                                         #
################################################################################

# Parse each team page
print('Parsing team pages')
cursor.callproc('get_teams', (None,))
results = cursor.fetchall()
while cursor.nextset() is not None: pass
connection.commit()
for result in results:
	print('\tTeam ' + str(result[0]))
	if result[0] >= 162683:
		print('\tDownloading...')
		cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
		cursor.execute("START TRANSACTION;")
		teamParser = TeamStorage(result[0], cursor)
		teamFile = urllib.urlopen('http://www.broomball.mtu.edu/team/view/' + str(result[0])).read().decode('utf8')
		teamParser.feed(teamFile)
		cursor.execute('COMMIT;')

################################################################################
# EOF                                                                          #
################################################################################