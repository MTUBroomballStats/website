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

class PlayerStorage(bbparser.PlayerParser):
	cursor = None
	playerNum = None
	
	def __init__(self, playerNum, cursor):
		bbparser.PlayerParser.__init__(self)
	
		self.playerNum = playerNum
		self.cursor = cursor
		
	def foundPlayer(self, userid, name):
		self.cursor.callproc('update_player', (self.playerNum, userid, name))
		while self.cursor.nextset() is not None: pass
		return self.playerNum
		
	def foundGame(self, pteamUrlNum, date, location, oteamUrlNum, teamgf, teamga, goals, assists, points, pims):
		print('\t\t\tGame against ' + str(oteamUrlNum))
		self.cursor.callproc('get_game_id', (date, location))
		row = self.cursor.fetchone()
		while row is None:
			if self.cursor.nextset() is None:
				break
			row = self.cursor.fetchone()
		if row is not None:
			gameid = row[0]
			while self.cursor.nextset() is not None: pass
			self.cursor.callproc('add_player_to_game', (gameid, self.playerNum, pteamUrlNum, goals, assists, pims))
			while self.cursor.nextset() is not None: pass
		
			return gameid
		return None

		
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
		
		print('\t\tPlayer ' + str(playerUrlNum))
		self.cursor.callproc('insert_player', (playerUrlNum, name))
		while self.cursor.nextset() is not None: pass
		self.cursor.callproc('add_player_to_team', (playerUrlNum, self.teamid, saves, goalieMins, goalsAgainst))
		while self.cursor.nextset() is not None: pass
		
		return playerUrlNum

		
class TeamListStorage(bbparser.SeasonParser):
	cursor = None
	year = None

	def __init__(self, year, cursor):
		bbparser.SeasonParser.__init__(self)
	
		self.cursor = cursor
		self.year = year

	def foundLeague(self, url, name):
		print('\t\tLeague ' + str(name))
		self.cursor.callproc('insert_league', (url, name, self.year))
		leagid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return leagid
		
	def foundConference(self, url, name, leagid):
		print('\t\t\tConference ' + str(name))
		self.cursor.callproc('insert_conference', (url, name, leagid))
		confid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return confid
		
	def foundTeam(self, leagid, confid, urlnum, name, wins, losses, ties, otlosses, gf, ga):
		print('\t\t\t\tTeam ' + str(urlnum))
		self.cursor.callproc('insert_team', (urlnum, name, confid))
		teamid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return teamid


class YearListStorage(bbparser.YearListParser):
	def __init__(self):
		bbparser.YearListParser.__init__(self)
		
		self.yearlist = set()
		
	def foundYear(self, year):
		print('\tYear ' + str(year))
		seasonStorage = TeamListStorage(year, cursor)
		seasonFile = urllib.urlopen('http://www.broomball.mtu.edu/teams/view/' + str(year)).read().decode('utf8')
		seasonStorage.feed(seasonFile)
		
	def getYearList(self):
		return yearlist
		

################################################################################
# MAIN                                                                         #
################################################################################

try:
	cursor.callproc('get_years')
	if len(cursor.fetchall()) == 0:
		while cursor.nextset() is not None: pass
		print('Parsing season pages')
		yearListParser = YearListStorage()
		yearListFile = urllib.urlopen('http://www.broomball.mtu.edu/teams/view/').read().decode('utf8')
		yearListParser.feed(yearListFile)
	
		connection.commit()
	else:
		while cursor.nextset() is not None: pass
		
	# Parse each team page
	print('Parsing team pages')
	cursor.callproc('get_teams', (None,))
	results = cursor.fetchall()
	while cursor.nextset() is not None: pass
	for result in results:
		print('\tTeam ' + str(result[0]))
		cursor.callproc('get_players', (result[0],))
		storedPlayers = len(cursor.fetchall())
		while cursor.nextset() is not None: pass
		connection.commit()
		if storedPlayers == 0:
			print('\tDownloading...')
			cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
			cursor.execute("START TRANSACTION;")
			teamParser = TeamStorage(result[0], cursor)
			teamFile = urllib.urlopen('http://www.broomball.mtu.edu/team/view/' + str(result[0])).read().decode('utf8')
			teamParser.feed(teamFile)
			cursor.execute('COMMIT;')

	# Parse each player page
	print('Parsing player pages')
	cursor.callproc('get_players', (None,))
	results = cursor.fetchall()
	while cursor.nextset() is not None: pass
	for result in results:
			print('\tPlayer ' + str(result[0]))
			cursor.callproc('get_appearances', (result[0],))
			storedAppearances = len(cursor.fetchall())
			while cursor.nextset() is not None: pass
			connection.commit()
			if storedAppearances == 0:
				cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
				cursor.execute("START TRANSACTION;")
				playerParser = PlayerStorage(result[0], cursor)
				playerFile = urllib.urlopen('http://broomball.mtu.edu/player/view/' + str(result[0])).read().decode('utf8')
				playerParser.feed(playerFile)
				cursor.execute('COMMIT;')

except:
	raise
	
finally:
	cursor.close()

################################################################################
# EOF                                                                          #
################################################################################