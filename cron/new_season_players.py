################################################################################
# new_season_players.py                                                        #
# Author: Will Weaver                                                          #
# Finds all players playing in a new season of broomball and updates their     #
# appearances.                                                                 #
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

# Parse each player page
print('Parsing player pages')
cursor.callproc('get_players', (datetime.today().year,))
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

################################################################################
# END OF FILE                                                                  #
################################################################################
