################################################################################
# update_results.py                                                            #
# author: Will Weaver                                                          #
# Retrieves any new results from broomball.mtu.edu and adds them to the db.    #
################################################################################

################################################################################
# IMPORTS                                                                      #
################################################################################

import bbparser
import json
import MySQLdb
import urllib
import datetime

################################################################################
# GLOBALS                                                                      #
################################################################################

cfg = open('config/update/db.cfg', 'r')
auth = json.loads(cfg.read())
cfg.close()
connection = MySQLdb.connect(	host=auth['host'],
								user=auth['user'],
								passwd=auth['passwd'],
								db=auth['db'],
								charset=auth['charset'])
del auth
del cfg
cursor = connection.cursor()

################################################################################
# CLASSES                                                                      #
################################################################################

class TeamInfoExtractor(bbparser.TeamParser):
	def __init__(self, urlnum, cursor):
		bbparser.TeamParser.__init__(self, urlnum)
		
		self.urlnum = urlnum
		self.cursor = cursor
		
		cursor.callproc('get_schedule', (self.urlnum,))
		self.dbGames = list()
		self.notOnlineGames = list()
		for result in cursor.fetchall():
			self.dbGames.append(result)
			self.notOnlineGames.append(result)
		while cursor.nextset() is not None: pass
		
		cursor.callproc('get_roster', (self.urlnum,))
		self.dbPlayers = list()
		self.notOnlinePlayers = list()
		for result in cursor.fetchall():
			self.dbPlayers.append(result)
			self.notOnlinePlayers.append(result)
		while cursor.nextset() is not None: pass
		
	def cleanUp(self):
		for notOnlineGame in self.notOnlineGames:
			cursor.callproc('cancel_game', (notOnlineGame[0],))
			while cursor.nextset() is not None: pass
			
		for notOnlinePlayer in self.notOnlinePlayers:
			cursor.callproc('drop_player', (notOnlinePlayer[0], self.urlnum))
			while cursor.nextset() is not None: pass

	def foundGame(self, opUrlNum, date, location, gf, ga, ha):
	
		if date is None or location is None:
			return
		
		# Check if this game isn't in the db when it should be
		webGameExists = False
		for dbGame in self.dbGames:
			if (date, location, opUrlNum) in (dbGame[1:4], dbGame[1:3] + (dbGame[5],)):
				webGameExists = True
				break
		if not webGameExists:
			cursor.callproc('insert_game', (self.urlnum, opUrlNum, date, location, gf, ga))
			while cursor.nextset() is not None: pass
		
		# Remove this game from the list of potentially cancelled games
		for notOnlineGame in self.notOnlineGames:
			if (date, location, opUrlNum) in (notOnlineGame[1:4], notOnlineGame[1:3] + (notOnlineGame[5],)):
				self.notOnlineGames.remove(notOnlineGame)
				break
		
		# Process played games
		if gf > 0 or ga > 0:
			self.cursor.callproc('play_game', (self.urlnum, gf, opUrlNum, ga))
			while cursor.nextset() is not None: pass

	def foundPlayer(self, playerUrlNum, name, goals, assists, points, pim, saves, goalieMins, goalsAgainst):
		
		# Check if this player isn't in the db when it should be
		webPlayerExists = False
		for dbPlayer in self.dbPlayers:
			if dbPlayer[0] == int(playerUrlNum):
				webPlayerExists = True
				break
		if not webPlayerExists:
			cursor.callproc('insert_player', (playerUrlNum, name))
			while cursor.nextset() is not None: pass
			cursor.callproc('add_player_to_team', (playerUrlNum, self.urlnum, saves, goalieMins, goalsAgainst))
			while cursor.nextset() is not None: pass

		# Remove this player from the list of players that have potentially left the roster
		for notOnlinePlayer in self.notOnlinePlayers:
			if notOnlinePlayer[0] == int(playerUrlNum):
				self.notOnlinePlayers.remove(notOnlinePlayer)
				break

################################################################################
# MAIN                                                                         #
################################################################################

# Get all teams from this year
cursor.callproc('get_teams', (datetime.date.today().year,))
results = cursor.fetchall()
while cursor.nextset() is not None: pass

# Update all teams from this year
for result in results:
	teamUrl = result[0]
	te = TeamInfoExtractor(teamUrl, cursor)
	teamFile = urllib.urlopen('http://www.broomball.mtu.edu/team/view/' + str(teamUrl)).read().decode('utf8')
	te.feed(teamFile)
	te.cleanUp()
	connection.commit()
	
cursor.callproc('update_appearances', ())
while cursor.nextset() is not None: pass

cursor.close()
connection.close()

################################################################################
# END OF FILE                                                                  #
################################################################################
