#!/usr/local/bin/python

################################################################################
# IMPORTS                                                                      #
################################################################################

import MySQLdb
import bbparser
import urllib
import re
import time

################################################################################
# CLASSES                                                                      #
################################################################################

class Player:
	def __init__(self, urlnum):
		self.urlnum = urlnum
		self.visited = False
		self.played_players = list()

	def add_played_player(self, other):
		self.played_players.append(other)

################################################################################
# GLOBALS                                                                      #
################################################################################

connection = MySQLdb.connect(host='localhost', user='whweaver_bbupdat', passwd='3m;*h,[Uke}e', db='whweaver_broomball', charset='utf8')
cursor = connection.cursor()

################################################################################
# MAIN                                                                         #
################################################################################

# Generate graph data structure
print("Generating graph data structure")
unvisited = dict()
cursor.callproc('get_players', (None,))
player_rows = cursor.fetchall()
while cursor.nextset() is not None: pass
for player_row in player_rows:
	print("\tPlayer: " + str(player_row[0]))
	if not player_row[0] in unvisited:
		cur_player = Player(player_row[0])
		unvisited[player_row[0]] = cur_player
	else:
		cur_player = unvisited[player_row[0]]
	cursor.callproc('get_players_played', (player_row[0],))
	player_played_rows = cursor.fetchall()
	while cursor.nextset() is not None: pass
	for player_played_row in player_played_rows:
		if not player_played_row[0] in unvisited:
			player_played = Player(player_played_row[0])
			unvisited[player_played_row[0]] = player_played
		else:
			player_played = unvisited[player_played_row[0]]
		cur_player.add_played_player(player_played)

components = list()
traversal = dict()

print("Checking connectedness")
# For every unvisited node c
while len(unvisited) > 0:
	print("\tNew component!")
	starter_player = unvisited.popitem()[1]

	# Create a new empty set of nodes, the current component
	cur_component = list()

	# Enqueue this node for traversal
	traversal[starter_player.urlnum] = starter_player

	# While there is any node t enqueued
	while len(traversal) > 0:

		# Remove this node (t) from the queue
		player = traversal.popitem()[1];

		# Mark every unvisited neighbor as open and enqueue it for traversal
		for played_player in player.played_players:
			if not played_player.visited and not played_player.urlnum in traversal:
				traversal[played_player.urlnum] = played_player

		# Mark this node as traversed
		player.visited = True
		if player.urlnum in unvisited:
			del unvisited[player.urlnum]

		# Add this node to the current component
		print("\t\t" + str(player.urlnum))
		cur_component.append(player)

	# Close the current component and add it to a list of components
	print("\tComponent of size " + str(len(cur_component)) + " found")
	components.append(cur_component)

################################################################################
# END OF FILE                                                                  #
################################################################################
