#!/usr/bin/python

print("Content-Type: application/json\n\n")

################################################################################
# get_teams_by_conference.py                                                   #
# Author: Will Weaver                                                          #
# Generates a JSON file containing the teams for a specified conference.     #
################################################################################

################################################################################
# IMPORTS                                                                      #
################################################################################

import cgi
import json
import MySQLdb

################################################################################
# GLOBALS                                                                      #
################################################################################

cfg = open('../../config/client/db.cfg', 'r')
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

conference = None
get_data = cgi.FieldStorage()
if "c" in get_data:
	conference = get_data["c"].value

cursor.callproc("get_teams_by_conference", (conference,))

teams = dict()
for result in cursor.fetchall():
	teams[result[0]] = result[1]

print(json.dumps(teams))

cursor.close()
connection.close()

################################################################################
# END OF FILE                                                                  #
################################################################################
