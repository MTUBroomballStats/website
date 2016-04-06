#!/usr/bin/python

print("Content-Type: application/json\n\n")

################################################################################
# get_leagues_by_year.py                                                       #
# Author: Will Weaver                                                          #
# Generates a JSON file containing the leagues for a specified year.           #
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

year = None
get_data = cgi.FieldStorage()
if "y" in get_data:
	year = get_data["y"].value

cursor.callproc("get_leagues_by_year", (year,))

leagues = dict()
for result in cursor.fetchall():
	leagues[result[0]] = result[1]

print(json.dumps(leagues))

cursor.close()
connection.close()

################################################################################
# END OF FILE                                                                  #
################################################################################
