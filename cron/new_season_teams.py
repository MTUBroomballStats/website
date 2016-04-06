################################################################################
# new_season_teams.py                                                          #
# Author: Will Weaver                                                          #
# Finds all teams from the current year and updates their schedules and        #
# rosters.                                                                     #
################################################################################

################################################################################
# IMPORTS                                                                      #
################################################################################

import MySQLdb
import urllib
import datetime
import new_season
import json

################################################################################
# GLOBALS                                                                      #
################################################################################

cfg = open('../config/update/db.cfg', 'r')
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
# MAIN                                                                         #
################################################################################
	
# Parse each team page
print('Parsing team pages')
cursor.callproc('get_teams', (datetime.today().year,))
results = cursor.fetchall()
while cursor.nextset() is not None: pass
for result in results:
	print('\tTeam ' + str(result[0]))
	cursor.callproc('get_players', (result[0],))
	storedPlayers = len(cursor.fetchall())
	while cursor.nextset() is not None: pass
	connection.commit()
	if storedPlayers == 0:
		cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;")
		cursor.execute("START TRANSACTION;")
		teamParser = TeamStorage(result[0], cursor)
		teamFile = urllib.urlopen('http://www.broomball.mtu.edu/team/view/' + str(result[0])).read().decode('utf8')
		teamParser.feed(teamFile)
		cursor.execute('COMMIT;')

################################################################################
# END OF FILE                                                                  #
################################################################################
