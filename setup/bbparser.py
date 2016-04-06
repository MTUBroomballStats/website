#!/usr/local/bin/python

################################################################################
# IMPORTS                                                                      #
################################################################################

import HTMLParser
import re
import datetime

################################################################################
# CONSTANTS                                                                    #
################################################################################

dateregex = re.compile('[A-Z][a-z]{2}, ([A-Z][a-z]{2}) ([1-3]?[0-9]) - (1?[0-9]):([0-9]{2}) ([ap])m')
monthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

################################################################################
# HELPER FUNCTIONS                                                             #
################################################################################

def datetimeParser(dtstring, year):
	match = dateregex.search(dtstring)
	month = monthList.index(match.group(1)) + 1
	day = int(match.group(2))
	prehour = int(match.group(3))
	minute = int(match.group(4))
	ap = match.group(5)
	
	if ap == 'p' and prehour != 12:
		hour = prehour + 12
	elif ap == 'a' and prehour == 12:
		hour = 0
	else:
		hour = prehour
		
	return datetime.datetime(year, month, day, hour, minute)

################################################################################
# YEAR LIST PARSER                                                             #
################################################################################

class YearListParser(HTMLParser.HTMLParser):
	state = None
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.state = None
		
	def handle_starttag(self, tag, attrs):
		if tag == 'select':
		
			# Enter selector
			for attr in attrs:
				if attr[0] == 'name' and attr[1] == 'season':
					self.state = 'in_selector'
					
		if tag == 'option':
		
			# Enter option
			if self.state == 'in_selector':
				self.state = 'ready_year'
	
	def handle_endtag(self, tag):
		if tag == 'select':
		
			# Exit selector
			if self.state == 'in_selector':
				self.state = None
				
		if tag == 'option':
			
			# Exit option
			if self.state == 'ready_exit_option':
				self.state = 'in_selector'
	
	def handle_data(self, data):
	
		# Get year
		if self.state == 'ready_year':
			self.foundYear(int(data))
			self.state = 'ready_exit_option'
			
	def foundYear(self, year):
		return None


################################################################################
# SEASON PARSER                                                                #
################################################################################

class SeasonParser(HTMLParser.HTMLParser):
	state = None
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.state = None
		self.curLeague = None
		self.curConf = None
		self.curTeamNum = None
		self.curTeamName = None
		self.curTeamWins = None
		self.curTeamLosses = None
		self.curTeamOtLosses = None
		self.curTeamTies = None
		self.curTeamPoints = None
		self.curTeamGf = None
		self.curTeamGa = None
	
	def handle_starttag(self, tag, attrs):
	
		if tag == 'div':
		
			# Enter main content container
			for attr in attrs:
				if attr[0] == 'id' and attr[1] == 'main_content_container':
					self.state = 'maincontentcontainer'
				
		if tag == 'h1':
		
			# Enter league name
			if self.state == 'maincontentcontainer' or self.state == 'ready_confurltag':
				self.state = 'ready_leagname'
				
			# Enter conference name
			if self.state == 'ready_confnametag':
				self.state = 'ready_confname'
		
		if tag == 'blockquote':
		
			# Enter league section
			if self.state == 'ready_leagblock':
				self.state = 'ready_confurltag1'
			
		if tag == 'tr':
		
			# Enter conference header
			if self.state == 'ready_confheader':
				for attr in attrs:
					if attr[0] == 'class' and attr[1] == 'header headerleft':
						self.state = 'conferenceheader'
						
			# Enter team row
			if self.state == 'conftable':
				self.state = 'ready_teamnamecell'
				
		if tag == 'td':
		
			# Enter conference header cell
			if self.state == 'conferenceheader':
				self.state = 'ready_confheadercell'
		
			# Enter team name cell
			if self.state == 'ready_teamnamecell':
				self.state = 'ready_teamnumtag'
				
			# Enter team win cell
			if self.state == 'ready_wincell':
				self.state = 'ready_wins'
				
			# Enter team loss cell
			if self.state == 'ready_losscell':
				self.state = 'ready_losses'
				
			# Enter team OT loss cell
			if self.state == 'ready_otcell':
				self.state = 'ready_ot'
				
			# Enter team points cell
			if self.state == 'ready_pointcell':
				self.state = 'ready_points'
				
			# Enter team GF cell
			if self.state == 'ready_gfcell':
				self.state = 'ready_gf'
				
			# Enter team GA cell
			if self.state == 'ready_gacell':
				self.state = 'ready_ga'
		
		if tag == 'a':
		
			# Handle conference URL
			if self.state == 'ready_confurltag1':
				for attr in attrs:
					if attr[0] == 'name':
						self.confUrl = attr[1]
						self.curLeague = self.foundLeague(self.confUrl, self.leagName)
				self.state = 'ready_exit_confurl'
			if self.state == 'ready_confurltag':
				for attr in attrs:
					if attr[0] == 'name':
						self.confUrl = attr[1]
				self.state = 'ready_exit_confurl'

			# Handle team number
			if self.state == 'ready_teamnumtag':
				for attr in attrs:
					if attr[0] == 'href':
						self.curTeamNum = int(attr[1][39:])
						self.state = 'ready_teamname'

	def handle_endtag(self, tag):
	
		if tag =='h1':
		
			# Exit league name
			if self.state == 'ready_exit_leagname':
				self.state = 'ready_leagblock'
				
			# Exit conference name
			if self.state == 'ready_exit_confname':
				self.state = 'ready_confheader'
			
		if tag == 'blockquote':
		
			# Exit league section
			if self.state == 'ready_exit_confname':
				self.state = 'maincontentcontainer'
			
		if tag == 'tr':
		
			# Exit conference header
			if self.state == 'conferenceheader':
				self.state = 'conftable'
				
			# Exit team row
			if self.state == 'ready_exit_teamrow':
				self.foundTeam(self.curLeague, self.curConf, self.curTeamNum, self.curTeamName, self.curTeamWins, self.curTeamLosses, self.curTeamTies, self.curTeamOtLosses, self.curTeamGf, self.curTeamGa)
				self.state = 'conftable'
				
		if tag == 'table':
		
			# Exit conference table
			if self.state == 'conftable':
				self.state = 'ready_confurltag'
			
		if tag == 'a':
			
			# Exit conference URL
			if self.state == 'ready_exit_confurl':
				self.state = 'ready_confnametag'

			# Exit team name
			if self.state == 'ready_exit_teamname':
				self.state = 'ready_exit_teamcell'
				
		if tag == 'td':
		
			# Exit conference header cell
			if self.state == 'ready_exit_confheadercell':
				self.state = 'conferenceheader'
		
			# Exit team cell
			if self.state == 'ready_exit_teamcell':
				self.state = 'ready_wincell'
				
			# Exit win cell
			if self.state == 'ready_exit_wincell':
				self.state = 'ready_losscell'
				
			# Exit loss cell
			if self.state == 'ready_exit_losscell':
				self.state = 'ready_otcell'
			
			# Exit overtime loss cell
			if self.state == 'ready_exit_otcell':
				self.state = 'ready_pointcell'
				
			# Exit point cell
			if self.state == 'ready_exit_pointcell':
				self.state = 'ready_gfcell'
			
			# Exit GF cell
			if self.state == 'ready_exit_gfcell':
				self.state = 'ready_gacell'
			
			# Exit GA cell
			if self.state == 'ready_exit_gacell':
				self.state = 'ready_exit_teamrow'

	def handle_data(self, data):
	
		# Get league name
		if self.state == 'ready_leagname':
			self.leagName = data.strip()
			self.state = 'ready_exit_leagname'
			
		# Get conference name
		if self.state == 'ready_confname':
			self.curConf = self.foundConference(self.confUrl, data.strip(), self.curLeague)
			self.state = 'ready_exit_confname'
			
		# Get conference header type
		if self.state == 'ready_confheadercell':
			if data.strip() == 'Overtime Losses':
				self.otType = 'otl'
			elif data.strip() == 'Ties':
				self.otType = 'tie'
			self.state = 'ready_exit_confheadercell'
			
		# Get team name
		if self.state == 'ready_teamname':
			self.curTeamName = data.strip()
			self.state = 'ready_exit_teamname'
			
		# Get team wins
		if self.state == 'ready_wins':
			self.curTeamWins = int(data.strip())
			self.state = 'ready_exit_wincell'
			
		# Get team losses
		if self.state == 'ready_losses':
			self.curTeamLosses = int(data.strip())
			self.state = 'ready_exit_losscell'
			
		# Get team overtime losses
		if self.state == 'ready_ot':
			if self.otType == 'otl':
				self.curTeamOtLosses = int(data.strip())
				self.curTeamTies = None
			elif self.otType == 'tie':
				self.curTeamTies = int(data.strip())
				self.curTeamOtLosses = None
			self.state = 'ready_exit_otcell'
			
		# Get team points
		if self.state == 'ready_points':
			self.curTeamPoints = int(data.strip())
			self.state = 'ready_exit_pointcell'
			
		# Get team GF
		if self.state == 'ready_gf':
			self.curTeamGf = int(data.strip())
			self.state = 'ready_exit_gfcell'
			
		# Get team GA
		if self.state == 'ready_ga':
			self.curTeamGa = int(data.strip())
			self.state = 'ready_exit_gacell'
			
	def foundLeague(self, name):
		return None
	
	def foundConference(self, url, name, leagid):
		return None
	
	def foundTeam(self, leagid, confid, urlnum, name, wins, losses, ties, otlosses, gf, ga):
		return None


################################################################################
# TEAM PARSER                                                                  #
################################################################################

class TeamParser(HTMLParser.HTMLParser):
	state = None
	nameregex = re.compile(r'View Team: (.*) \((20[0-9]{2})\)')
	
	def __init__(self, teamUrlNum):
		HTMLParser.HTMLParser.__init__(self)
		
		self.state = None
		self.teamUrlNum = teamUrlNum
		self.year = None
		self.name = None
		self.curGameDateTime = None
		self.curGameLocation = None
		self.curGameOp = None
		self.curGameGf = None
		self.curGameGa = None
		self.curGameHa = None
		
		self.curPlayerNum = None
		self.curPlayerName = None
		self.curPlayerGoals = None
		self.curPlayerAssists = None
		self.curPlayerPoints = None
		self.curPlayerPims = None
		self.curPlayerSaves = None
		self.curPlayerGoalieMins = None
		self.curPlayerGa = None
		
	def handle_starttag(self, tag, attrs):
	
		if tag == 'h1':
		
			# Enter Schedule or Roster header
			if self.state == 'maincontentcontainer':
				self.state = 'ready_sectionheader'
	
		if tag == 'div':
		
			# Enter main content container
			for attr in attrs:
				if attr[0] == 'id' and attr[1] == 'main_content_container':
					self.state = 'maincontentcontainer'
					
			# Enter team name
			for attr in attrs:
				if attr[0] == 'id' and attr[1] == 'title_bar_content':
					self.state = 'teamname'
					
		if tag == 'tr':
		
			# Enter games header
			if self.state == 'ready_schedule':
				for attr in attrs:
					if attr[0] == 'class' and attr[1] == 'header headerleft':
						self.state = 'gamesheader'
			
			# Enter game row
			if self.state == 'gamestable':
				self.state = 'gamerow'
				
			# Enter roster header
			if self.state == 'ready_roster':
				for attr in attrs:
					if attr[0] == 'class' and attr[1] == 'header headerleft':
						self.state = 'rosterheader'
						
			# Enter player row
			if self.state == 'rostertable':
				self.state = 'playerrow'
				
		if tag == 'td':
		
			##################
			# Schedule cells #
			##################
			
			# Enter datetime
			if self.state == 'gamerow':
				for attr in attrs:
					if attr[0] == 'colspan' and attr[1] == '2':
						self.curGameDateTime = None
						self.curGameLocation = None
						self.state = 'ready_exit_locationcell'
				if self.state != 'ready_exit_locationcell':
					self.state = 'ready_datetime'
				
			# Enter location
			if self.state == 'ready_locationcell':
				self.state = 'ready_location'
				
			# Enter home
			if self.state == 'ready_homecell':
				self.state = 'ready_hometag'
				
			# Enter home goals
			if self.state == 'ready_homegoalcell':
				self.state = 'ready_homegoals'
				
			# Enter visitor goals
			if self.state == 'ready_visitorgoalcell':
				self.state = 'ready_visitorgoals'
				
			# Enter visitor
			if self.state == 'ready_visitorcell':
				self.state = 'ready_visitortag'
				
			# Enter video cell
			if self.state == 'ready_videocell':
				self.state = 'ready_exit_videocell'
				
			################
			# ROSTER CELLS #
			################
				
			# Enter number tag
			if self.state == 'playerrow':
				self.state = 'ready_playertag'
			
			# Enter goals
			if self.state == 'ready_goalcell':
				self.state = 'ready_goals'
			
			# Enter assists
			if self.state == 'ready_assistcell':
				self.state = 'ready_assists'
			
			# Enter points
			if self.state == 'ready_pointcell':
				self.state = 'ready_points'
			
			# Enter pims
			if self.state == 'ready_pimcell':
				self.state = 'ready_pims'
			
			# Enter saves
			if self.state == 'ready_savecell':
				self.state = 'ready_saves'
			
			# Enter goalie mins
			if self.state == 'ready_goaliemincell':
				self.state = 'ready_goaliemins'
			
			# Enter goals against
			if self.state == 'ready_gacell':
				self.state = 'ready_ga'
				
		if tag == 'a':
			
			# Get home number
			if self.state == 'ready_hometag':
				for attr in attrs:
					if attr[0] == 'href':
						homeNum = int(attr[1][39:])
				if homeNum == self.teamUrlNum:
					self.curGameHa = 'h'
				else:
					self.curGameHa = 'a'
					self.curGameOp = homeNum
				self.state = 'ready_exit_hometag'
					
			# Get visitor number
			if self.state == 'ready_visitortag':
				if self.curGameHa == 'h':
					for attr in attrs:
						if attr[0] == 'href':
							visitorNum = int(attr[1][39:])
					self.curGameOp = visitorNum
				self.state = 'ready_exit_visitortag'
				
			# Get player number
			if self.state == 'ready_playertag':
				for attr in attrs:
					if attr[0] == 'href':
						self.curPlayerNum = attr[1][41:]
				self.state = 'ready_playername'
	
	def handle_endtag(self, tag):
	
		if tag == 'h1':
		
			# Exit schedule header
			if self.state == 'ready_exit_scheduleheader':
				self.state = 'ready_schedule'
				
			# Exit roster header
			if self.state == 'ready_exit_rosterheader':
				self.state = 'ready_roster'
		
		if tag == 'div':
			
			# Exit main content container
			if self.state == 'maincontentcontainer':
				self.state = None
				
			# Exit team name
			if self.state == 'teamname_next':
				name = ''
				for part in self.name:
					name = name + part
				match = self.nameregex.search(name)
				self.name = match.group(1)
				self.year = int(match.group(2))
				self.state = None
				
		if tag == 'tr':
		
			# Exit games header
			if self.state == 'gamesheader':
				self.state = 'gamestable'
				
			# Exit game row
			if self.state == 'gamerow':
				self.foundGame(self.curGameOp, self.curGameDateTime, self.curGameLocation, self.curGameGf, self.curGameGa, self.curGameHa)
				self.state = 'gamestable'
				
			# Exit roster header
			if self.state == 'rosterheader':
				self.state = 'rostertable'
				
			if self.state == 'playerrow':
				self.foundPlayer(self.curPlayerNum, self.curPlayerName, self.curPlayerGoals, self.curPlayerAssists, self.curPlayerPoints, self.curPlayerPims, self.curPlayerSaves, self.curPlayerGoalieMins, self.curPlayerGa)
				self.state = 'rostertable'
				
		if tag == 'table':
			
			# Exit game table
			if self.state == 'gamestable':
				self.state = 'maincontentcontainer'
				
			if self.state == 'rostertable':
				self.state = 'maincontentcontainer'
				
		if tag == 'td':
		
			##################
			# SCHEDULE CELLS #
			##################
			
			# Exit datetime cell
			if self.state == 'ready_exit_datetimecell':
				self.state = 'ready_locationcell'
				
			# Exit location cell
			if self.state == 'ready_exit_locationcell':
				self.state = 'ready_homecell'
				
			# Exit home cell
			if self.state == 'ready_exit_homecell':
				self.state = 'ready_homegoalcell'
				
			# Exit home goal cell
			if self.state == 'ready_exit_homegoalcell':
				self.state = 'ready_visitorgoalcell'
				
			# Exit visitor goal cell
			if self.state == 'ready_exit_visitorgoalcell':
				self.state = 'ready_visitorcell'
				
			# Exit visitor cell
			if self.state == 'ready_exit_visitorcell':
				self.state = 'ready_videocell'
				
			# Exit video cell
			if self.state == 'ready_exit_videocell':
				self.state = 'gamerow'
				
			################
			# ROSTER CELLS #
			################
			
			# Exit name cell
			if self.state == 'ready_exit_namecell':
				self.state = 'ready_goalcell'
			
			# Exit goal cell
			if self.state == 'ready_exit_goalcell':
				self.state = 'ready_assistcell'
			
			# Exit assist cell
			if self.state == 'ready_exit_assistcell':
				self.state = 'ready_pointcell'
			
			# Exit point cell
			if self.state == 'ready_exit_pointcell':
				self.state = 'ready_pimcell'
			
			# Exit pim cell
			if self.state == 'ready_exit_pimcell':
				self.state = 'ready_savecell'
			
			# Exit save cell
			if self.state == 'ready_exit_savecell':
				self.state = 'ready_goaliemincell'
			
			# Exit goalie min cell
			if self.state == 'ready_exit_goaliemincell':
				self.state = 'ready_gacell'
			
			# Exit goals against cell
			if self.state == 'ready_exit_gacell':
				self.state = 'playerrow'
				
		if tag == 'a':
		
			# Exit home tag
			if self.state == 'ready_exit_hometag':
				self.state = 'ready_exit_homecell'
				
			# Exit visitor tag
			if self.state == 'ready_exit_visitortag':
				self.state = 'ready_exit_visitorcell'
				
			# Exit player tag
			if self.state == 'ready_exit_playertag':
				self.state = 'ready_exit_namecell'
			
	def handle_data(self, data):
	
		##################
		# SCHEDULE CELLS #
		##################
	
		if self.state == 'ready_sectionheader':
		
			# Get schedule header
			if data == 'Team Schedule':
				self.state = 'ready_exit_scheduleheader'
			
			# Get roster header
			if data == 'Team Roster':
				self.state = 'ready_exit_rosterheader'
		
		# Get other part of team name
		if self.state == 'teamname_next':
			self.name.append(data)
		
		# Get team name
		if self.state == 'teamname':
			self.name = [data]
			self.state = 'teamname_next'
	
		# Get date
		if self.state == 'ready_datetime':
			self.curGameDateTime = datetimeParser(data.strip(), self.year)
			self.state = 'ready_exit_datetimecell'
			
		# Get location
		if self.state == 'ready_location':
			self.curGameLocation = data.strip()
			self.state = 'ready_exit_locationcell'
		
		# Get home goals
		if self.state == 'ready_homegoals':
			if self.curGameHa == 'h':
				if self.curGameDateTime == None:
					self.curGameGf = None
				else:
					if self.curGameDateTime < datetime.datetime.today():
						self.curGameGf = int(data.strip())
					else:
						self.curGameGf = None
			elif self.curGameHa == 'a':
				if self.curGameDateTime == None:
					self.curGameGa = None
				else:
					if self.curGameDateTime < datetime.datetime.today():
						self.curGameGa = int(data.strip())
					else:
						self.curGameGa = None
			self.state = 'ready_exit_homegoalcell'
				
		# Get visitor goals
		if self.state == 'ready_visitorgoals':
			if self.curGameHa == 'h':
				if self.curGameDateTime == None:
					self.curGameGa = None
				else:
					if self.curGameDateTime < datetime.datetime.today():
						self.curGameGa = int(data.strip())
					else:
						self.curGameGa = None
			elif self.curGameHa == 'a':
				if self.curGameDateTime == None:
					self.curGameGf = None
				else:
					if self.curGameDateTime < datetime.datetime.today():
						self.curGameGf = int(data.strip())
					else:
						self.curGameGf = None
			self.state = 'ready_exit_visitorgoalcell'
			
		################
		# ROSTER CELLS #
		################
				
		# Get player name
		if self.state == 'ready_playername':
			self.curPlayerName = data.strip()
			self.state = 'ready_exit_playertag'
		
		# Get player goals
		if self.state == 'ready_goals':
			self.curPlayerGoals = int(data.strip())
			self.state = 'ready_exit_goalcell'
		
		# Get player assists
		if self.state == 'ready_assists':
			self.curPlayerAssists = int(data.strip())
			self.state = 'ready_exit_assistcell'
		
		# Get player points
		if self.state == 'ready_points':
			self.curPlayerPoints = int(data.strip())
			self.state = 'ready_exit_pointcell'
		
		# Get player pims
		if self.state == 'ready_pims':
			self.curPlayerPims = int(data.strip())
			self.state = 'ready_exit_pimcell'
		
		# Get player saves
		if self.state == 'ready_saves':
			self.curPlayerSaves = int(data.strip())
			self.state = 'ready_exit_savecell'
		
		# Get player goalie mins
		if self.state == 'ready_goaliemins':
			self.curPlayerGoalieMins = int(data.strip())
			self.state = 'ready_exit_goaliemincell'
		
		# Get player goals against
		if self.state == 'ready_ga':
			self.curPlayerGa = int(data.strip())
			self.state = 'ready_exit_gacell'
							
	def foundGame(self, opUrlNum, date, location, gf, ga, ha):
		return None
	
	def foundPlayer(self, playerUrlNum, name, goals, assists, points, pim, saves, goalieMins, goalsAgainst):
		return None
	

################################################################################
# PLAYER PARSER                                                                #
################################################################################

class PlayerParser(HTMLParser.HTMLParser):
	state = None
	titleRegex = re.compile(r'View Player: (.*) \((.*)\)')
	scoreRegex = re.compile(r'([0-9]+) - ([0-9]+)')
	
	
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		
		self.state = None
		self.playerName = None
		self.playerId = None
		self.curYear = None
		self.curTeamId = None
		self.curGameDateTime = None
		self.curGameLocation = None
		self.curGameOp = None
		self.curGameGf = None
		self.curGameGa = None
		self.curGameGoals = None
		self.curGameAssists = None
		self.curGamePoints = None
		self.curGamePim = None
	
	
	def handle_starttag(self, tag, attrs):
	
		if tag == 'div':
			for attr in attrs:
				if attr[0] == 'id':
				
					# Enter name and userid cell
					if attr[1] == 'title_bar_content':
						self.state = 'ready_nameid'
						
					# Enter main content container
					if attr[1] == 'main_content_container':
						self.state = 'maincontentcontainer'
						
		if tag == 'h1':
			
			# Enter year label
			if self.state == 'maincontentcontainer':
				self.state = 'ready_year'
				
		if tag == 'blockquote':
		
			# Enter year
			if self.state == 'ready_yearsection':
				self.state = 'year'
				
		if tag == 'h1':
		
			# Enter team cell
			if self.state == 'year':
				self.state = 'ready_teamtag'
				
		if tag == 'a':
		
			# Get team id
			if self.state == 'ready_teamtag':
				for attr in attrs:
					if attr[0] == 'href':
						self.curTeamId = int(attr[1][39:])
				self.state = 'ready_exit_teamname'
				
			# Get opponent id
			if self.state == 'ready_optag':
				for attr in attrs:
					if attr[0] == 'href':
						self.curGameOp = int(attr[1][39:])
				self.state = 'ready_exit_optag'
				
		if tag == 'table':
		
			# Enter team table
			if self.state == 'ready_teamtable':
				self.state = 'ready_teamheaderrow'
				
		if tag == 'tr':
		
			# Enter team header row
			if self.state == 'ready_teamheaderrow':
				self.state = 'teamheaderrow'
				
			# Enter game row
			if self.state == 'teamtable':
				for attr in attrs:
					if attr[0] == 'class':
						if attr[1] == 'footer footerleft':
							self.state = 'teamtotalrow'
				if self.state != 'teamtotalrow':
					self.state = 'gamerow'
				
		if tag == 'td':
		
			# Enter date/time cell
			if self.state == 'gamerow':
				self.state = 'ready_datetime'
				
			# Enter location cell
			if self.state == 'ready_locationcell':
				self.state = 'ready_location'
				
			# Enter opponent cell
			if self.state == 'ready_opcell':
				self.state = 'ready_optag'
				
			# Enter score cell
			if self.state == 'ready_scorecell':
				self.state = 'ready_score'
				
			# Enter goal cell
			if self.state == 'ready_goalcell':
				self.state = 'ready_goals'
				
			# Enter assist cell
			if self.state == 'ready_assistcell':
				self.state = 'ready_assists'
				
			# Enter point cell
			if self.state == 'ready_pointcell':
				self.state = 'ready_points'
				
			# Enter penalty minute cell
			if self.state == 'ready_pimcell':
				self.state = 'ready_pim'
				
			# Enter video cell
			if self.state == 'ready_videocell':
				self.state = 'ready_exit_videocell'
	
	
	def handle_endtag(self, tag):
	
		if tag == 'div':
		
			# Exit player name and ID cell
			if self.state == 'ready_exit_nameid':
				self.state = None
				
			# Exit main content container
			if self.state == 'maincontentcontainer':
				self.state = None
		
		if tag == 'blockquote':
		
			# Exit year
			if self.state == 'year':
				self.state = 'maincontentcontainer'
				
		if tag == 'h1':
		
			# Exit year label
			if self.state == 'ready_exit_year':
				self.state = 'ready_yearsection'
		
			# Exit team name and ID cell
			if self.state == 'ready_exit_teamtag':
				self.state = 'ready_teamtable'
				
		if tag == 'a':
		
			# Exit team name link
			if self.state == 'ready_exit_teamname':
				self.state = 'ready_exit_teamtag'
				
			# Exit opponent name link
			if self.state == 'ready_exit_optag':
				self.state = 'ready_exit_opcell'
				
		if tag == 'table':
		
			# Exit team game table
			if self.state == 'teamtable':
				self.state = 'year'
				
		if tag == 'tr':
		
			# Exit team header row
			if self.state == 'teamheaderrow':
				self.state = 'teamtable'
				
			# Exit game row
			if self.state == 'gamerow':
				self.foundGame(self.curTeamId, self.curGameDateTime, self.curGameLocation, self.curGameOp, self.curGameGf, self.curGameGa, self.curGameGoals, self.curGameAssists, self.curGamePoints, self.curGamePim)
				self.state = 'teamtable'
				
			# Exit team total row
			if self.state == 'teamtotalrow':
				self.state = 'teamtable'
				
		if tag == 'td':
			
			# Exit date/time cell
			if self.state == 'ready_exit_datetimecell':
				self.state = 'ready_locationcell'
			
			# Exit location cell
			if self.state == 'ready_exit_locationcell':
				self.state = 'ready_opcell'
			if self.state == 'ready_location':
				self.curGameLocation = None
				self.state = 'ready_opcell'
			
			# Exit opponent cell
			if self.state == 'ready_exit_opcell':
				self.state = 'ready_scorecell'
				
			# Exit score cell
			if self.state == 'ready_exit_scorecell':
				self.state = 'ready_goalcell'
				
			# Exit goal cell
			if self.state == 'ready_exit_goalcell':
				self.state = 'ready_assistcell'
				
			# Exit assist cell
			if self.state == 'ready_exit_assistcell':
				self.state = 'ready_pointcell'
				
			# Exit point cell
			if self.state == 'ready_exit_pointcell':
				self.state = 'ready_pimcell'
				
			# Exit penalty minute cell
			if self.state == 'ready_exit_pimcell':
				self.state = 'ready_videocell'
				
			# Exit video cell
			if self.state == 'ready_exit_videocell':
				self.state = 'gamerow'
	
	
	def handle_data(self, data):
	
		# Get player name and user ID
		if self.state == 'ready_nameid':
			match = self.titleRegex.search(data.strip())
			if match:
				self.playerName = match.group(1)
				self.playerId = match.group(2)
			else:
				self.playerName = 'Covert Player'
				self.playerId = None
			self.foundPlayer(self.playerId, self.playerName)
			self.state = 'ready_exit_nameid'
			
		# Get year
		if self.state == 'ready_year':
			self.curYear = int(data.strip())
			self.state = 'ready_exit_year'
			
		# Get game date/time
		if self.state == 'ready_datetime':
			if data.strip() == 'Canceled':
				self.curGameDateTime = None
			else:
				self.curGameDateTime = datetimeParser(data.strip(), self.curYear)
			self.state = 'ready_exit_datetimecell'
			
		# Get game location
		if self.state == 'ready_location':
			self.curGameLocation = data.strip()
			self.state = 'ready_exit_locationcell'
			
		# Get game score
		if self.state == 'ready_score':
			match = self.scoreRegex.search(data.strip())
			if match:
				self.curGameGf = match.group(1)
				self.curGameGa = match.group(2)
			else:
				self.curGameGf = None
				self.curGameGa = None
			self.state = 'ready_exit_scorecell'
			
		# Get goals
		if self.state == 'ready_goals':
			self.curGameGoals = int(data.strip())
			self.state = 'ready_exit_goalcell'
			
		# Get assists
		if self.state == 'ready_assists':
			self.curGameAssists = int(data.strip())
			self.state = 'ready_exit_assistcell'
			
		# Get points
		if self.state == 'ready_points':
			self.curGamePoints = int(data.strip())
			self.state = 'ready_exit_pointcell'
			
		# Get penalty minutes
		if self.state == 'ready_pim':
			self.curGamePim = int(data.strip())
			self.state = 'ready_exit_pimcell'
	
	
	def foundPlayer(self, userid, name):
		return None

		
	def foundGame(self, pteamUrlNum, date, location, oteamUrlNum, teamgf, teamga, goals, assists, points, pims):
		return None

	
################################################################################
# EOF                                                                          #
################################################################################