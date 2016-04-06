#!/usr/bin/python

print("Content-Type: application/json\n\n")

################################################################################
# get_conferences_by_league.py                                                 #
# Author: Will Weaver                                                          #
# Generates a JSON file containing the conferences for a specified league.     #
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

league = None
get_data = cgi.FieldStorage()
if "l" in get_data:
	league = get_data["l"].value

cursor.callproc("get_conferences_by_league", (league,))

conferences = dict()
for result in cursor.fetchall():
	conferences[result[0]] = result[1]

print(json.dumps(conferences))

cursor.close()
connection.close()

################################################################################
# END OF FILE                                                                  #
################################################################################
