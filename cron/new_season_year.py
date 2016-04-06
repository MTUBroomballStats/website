################################################################################
# new_season_year.py                                                           #
# Author: Will Weaver                                                          #
# Identifies all teams in a new year and puts them in the database.            #
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
# FUNCTIONS                                                                    #
################################################################################

################################################################################
# MAIN                                                                         #
################################################################################

cursor.callproc('get_teams', (datetime.today().year,))
if len(cursor.fetchall()) == 0:
	while cursor.nextset() is not None: pass
	print('Parsing season pages')
	seasonParser = TeamListStorage()
	seasonFile = urllib.urlopen('http://www.broomball.mtu.edu/teams/view/' + str(datetime.today().year)).read().decode('utf8')
	seasonParser.feed(yearListFile)

	connection.commit()
else:
	while cursor.nextset() is not None: pass

################################################################################
# END OF FILE                                                                  #
################################################################################
