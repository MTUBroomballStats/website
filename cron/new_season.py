################################################################################
# new_season.py                                                                #
# Author: Will Weaver                                                          #
# Provides classes used for parsing a new season of broomball.                 #
################################################################################

################################################################################
# IMPORTS                                                                      #
################################################################################

import bbparser

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

	def foundLeague(self, name):
		print('\t\tLeague ' + str(name))
		self.cursor.callproc('insert_league', (name, self.year))
		leagid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return leagid
		
	def foundConference(self, name, leagid):
		print('\t\t\tConference ' + str(name))
		self.cursor.callproc('insert_conference', (name, leagid))
		confid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return confid
		
	def foundTeam(self, leagid, confid, urlnum, name, wins, losses, ties, otlosses, gf, ga):
		print('\t\t\t\tTeam ' + str(urlnum))
		self.cursor.callproc('insert_team', (urlnum, name, confid))
		teamid = self.cursor.fetchone()[0]
		while self.cursor.nextset() is not None: pass
		return teamid

################################################################################
# END OF FILE                                                                  #
################################################################################
