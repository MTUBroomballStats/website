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

################################################################################
# GLOBALS                                                                      #
################################################################################

connection = MySQLdb.connect(	host='localhost',
								user='whweaver_bbclien',
								passwd='5K1?;,men.s1',
								db='whweaver_broomball',
								charset='utf8')
cursor = connection.cursor()

################################################################################
# MAIN                                                                         #
################################################################################

try:
	i = 0
	while(True):
		print("Iterating ratings (" + str(i) + ")")
		cursor.callproc("iterate_ratings", ())
		connection.commit()
		i += 1

except:
	pass

finally:
	cursor.close()
	connection.close()
	print("Finished!")

################################################################################
# END OF FILE                                                                  #
################################################################################
