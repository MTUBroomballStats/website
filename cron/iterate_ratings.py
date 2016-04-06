#!/usr/bin/python

################################################################################
# iterate_ratings.py                                                           #
# Author: Will Weaver                                                          #
# Schedulable wrapper for the MySQL procedure of the same name                 #
################################################################################

################################################################################
# IMPORTS                                                                      #
################################################################################

import MySQLdb
import json
import datetime
import _mysql_exceptions

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
# MAIN                                                                         #
################################################################################

try:
	cursor.callproc("get_years")
	results = cursor.fetchall()
	while cursor.nextset() is not None: pass

	for i in range(4):
		for result in results:
			while (1):
				try:
					cursor.callproc("iterate_ratings", (result[0],))
					break;
				except _mysql_exceptions.OperationalError as e:
					continue;
			connection.commit()

except:
	raise

finally:
	cursor.close()
	connection.close()

################################################################################
# END OF FILE                                                                  #
################################################################################
