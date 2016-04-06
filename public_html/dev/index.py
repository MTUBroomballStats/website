#!/usr/bin/python

print("Content-Type: text/html\n\n")

################################################################################
# index.py                                                                     #
# Author: Will Weaver                                                          #
# Generates default HTML for mtubroomballstats.com                             #
################################################################################

################################################################################
# IMPORTS                                                                      #
################################################################################

import MySQLdb
import cgi
import cgitb
import collections
import json

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

ENTITIES = collections.OrderedDict()
ENTITIES["t"] = "Teams"
ENTITIES["p"] = "Players"
ENTITIES["c"] = "Conferences"
ENTITIES["l"] = "Leagues"

################################################################################
# FUNCTIONS                                                                    #
################################################################################

def createHTMLRow(entity, rank, result):
	# Team result: (urlnum, name, wins, losses, ties, goalsFor, goalsAgainst, rating)
	# Player result: (urlnum, name, wins, losses, ties, goals, assists, rating)
	# Conference result: (id, url, season, name, rating)
	# League result: (id, url, season, name, rating)

	# Row style information
	row = unicode("<tr")
	if rank % 2 == 0:
		row += unicode(" class=\"altrow\">\n")
	else:
		row += unicode(">\n")

	# Rank
	row += unicode("<td class=\"rank_cell\">") + unicode(rank) + unicode("</td>\n")

	# Name
	if entity == "t":
		row += unicode("<td class=\"name_cell\"><a href=\"http://www.broomball.mtu.edu/team/view/")
	elif entity == "p":
		row += unicode("<td class=\"name_cell\"><a href=\"http://www.broomball.mtu.edu/player/view/")
	else:
		row += unicode("<td class=\"name_cell\"><a href=\"http://www.broomball.mtu.edu/teams/view/")
	if entity in ("t", "p"):
		row += unicode(result[0])
		row += unicode("\" class=\"name_cell\">")
		row += unicode(result[1])
	else:
		row += unicode(result[1])
		row += unicode("\" class=\"name_cell\">")
		row += unicode(result[3])
	row += unicode("</td>\n")

	# Record
	if entity in ("t", "p"):
		row += unicode("<td class=\"stats_cell\">")
		row += unicode(result[2]) + unicode("-") + unicode(result[3]) + unicode("-") + unicode(result[4])
		row += unicode("</td>\n")

		# Goals For
		row += unicode("<td class=\"stats_cell\">") + unicode(result[5]) + unicode("</td>\n")

		# Goals Against
		row += unicode("<td class=\"stats_cell\">") + unicode(result[6]) + unicode("</td>\n")

		# Rating
		row += unicode("<td class=\"stats_cell\">") + unicode(result[7]) + unicode("</td>\n")
	else:
		# Rating
		row += unicode("<td class=\"stats_cell\">") + unicode(result[4]) + unicode("</td>\n")

	# Other links
	if entity != "p":
		row += unicode("<td class=\"stats_cell\">")
	if entity == "l":
		row += unicode("</a> <a href=\"http://www.mtubroomballstats.com/?e=c&l=")
		row += unicode(result[0])
		row += unicode("\">[c]</a>")
		row += unicode("</a> <a href=\"http://www.mtubroomballstats.com/?e=t&l=")
		row += unicode(result[0])
		row += unicode("\">[t]</a>")
		row += unicode("</a> <a href=\"http://www.mtubroomballstats.com/?e=p&l=")
		row += unicode(result[0])
		row += unicode("\">[p]</a>")
	if entity == "c":
		row += unicode("</a> <a href=\"http://www.mtubroomballstats.com/?e=t&c=")
		row += unicode(result[0])
		row += unicode("\">[t]</a>")
		row += unicode("</a> <a href=\"http://www.mtubroomballstats.com/?e=p&c=")
		row += unicode(result[0])
		row += unicode("\">[p]</a>")
	if entity == "t":
		row += unicode("</a> <a href=\"http://www.mtubroomballstats.com/?e=p&t=")
		row += unicode(result[0])
		row += unicode("\">[p]</a>")
	if entity != "p":
		row += unicode("</td>")

	# Ending tag
	row += unicode("</tr>\n")

	return row

################################################################################
# MAIN                                                                         #
################################################################################

cgitb.enable()

selected_team = None
selected_conference = None
selected_league = None
selected_year = None
selected_entity = None

# Get the desired ranking parameters from the GET variables
get_data = cgi.FieldStorage()
if "e" in get_data:
	selected_entity = get_data["e"].value
if "y" in get_data:
	selected_year = get_data["y"].value
if "l" in get_data and selected_entity in ("t", "p", "c"):
	selected_league = get_data["l"].value
if "c" in get_data and selected_entity in ("t", "p"):
	selected_conference = get_data["c"].value
if "t" in get_data and selected_entity in ("p"):
	selected_team = get_data["t"].value

# Assume we're ranking teams if no entity is specified
if selected_entity is None:
	selected_entity = "t"

# If a single parameter is specified, fill it its information
if selected_team is not None and selected_team != "a":
	cursor.callproc('get_full_team', (selected_team,))
	result = cursor.fetchone()
	selected_conference = result[1]
	selected_league = result[2]
	selected_year = result[3]
elif selected_conference is not None and selected_conference != "a":
	cursor.callproc('get_full_conference', (selected_conference,))
	result = cursor.fetchone()
	selected_league = result[1]
	selected_year = result[2]
elif selected_league is not None and selected_league != "a":
	cursor.callproc('get_full_league', (selected_league,))
	result = cursor.fetchone()
	selected_year = result[1]
while cursor.nextset() is not None: pass

#print(selected_entity)
#print(selected_team)
#print(selected_conference)
#print(selected_league)
#print(selected_year)

#exit(0)

print("""
<html>
<head>
	<link rel="shortcut icon" href="icon3.png" type="image/png">
	<title>MTU Broomball Stats</title>
	<!-- TODO: Meta -->
	<meta charset="UTF-8">
	<link rel="stylesheet" type="text/css" href="styles.css" />
	<script>
	  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
	  ga('create', 'UA-48515854-1', 'mtubroomballstats.com');
	  ga('send', 'pageview');

	</script>
	<script src="scripts.js"></script>
</head>

<body>
	<div id="page_container">
		<div id="page_header">
			<div id="logo">
				<a href="index.py" id="templogo">MTU Broomball Stats</a>
			</div>
		</div>
			
		<!-- Page Content -->
		<div id="page_content">
			<form name="data_type">
				<span class="filter_menu" id="span_entity">
					Rank: 
					<select name="e" id="select_entity" onchange="change_entity()" style="display:inline">""")

for e in ENTITIES:
	option = "<option value=\"" + str(e) + "\""
	if e == selected_entity:
		option += " selected=\"selected\""
	option += ">" + str(ENTITIES[e]) + "</option>"
	print(option)

print("""
					</select>
				</span>
				
				<span class="filter_menu" id="span_year">
					Year: 
					<select name="y" id="select_year" onchange="change_year()" style="display:inline">""")

option = "<option value=\"a\""
if selected_year == "a":
	option += " selected=\"selected\""
option += ">All Years</option>"
print(option)

cursor.callproc("get_years_desc", ())
for result in cursor.fetchall():
	if selected_year is None:
		selected_year = result[0]
	option = "<option value=\"" + str(result[0]) + "\""
	if str(selected_year) == str(result[0]):
		option += " selected=\"selected\""
	option += ">" + str(result[1]).encode("UTF-8") + "</option>"
	print(option)
while cursor.nextset() is not None: pass

print("""
					</select>
				</span>""")

if selected_entity in ("t", "p", "c"):
	print("<span class=\"filter_menu\" id=\"span_league\" style=\"display:inline\">")
else:
	print("<span class=\"filter_menu\" id=\"span_league\" style=\"display:none\">")
				
print("""<br />
					League:
					<select name="l" id="select_league" onchange="change_league()" style="display:inline">""")

if selected_league is None or selected_league == "a":
	print("<option value=\"a\" selected=\"selected\">All Leagues</option>")
else:
	print("<option value=\"a\">All Leagues</option>")

if selected_year is not None and selected_year != "a":
	cursor.callproc("get_leagues_by_year", (selected_year,))
	for result in cursor.fetchall():
		option = "<option value=\"" + str(result[0]) + "\""
		if str(selected_league) == str(result[0]):
			option += " selected=\"selected\""
		option += ">" + unicode(result[1]).encode("UTF-8") + "</option>"
		print(option)
	while cursor.nextset() is not None: pass

print("""
					</select>
				</span>""")

if selected_entity in ("p", "t"):
	print("<span class=\"filter_menu\" id=\"span_conference\" style=\"display:inline\">")
else:
	print("<span class=\"filter_menu\" id=\"span_conference\" style=\"display:none\">")
				
print("""
					Conference:
					<select name="c" id="select_conference" onchange="change_conference()" style="display:inline">""")

if selected_conference is None or selected_conference == "a":
	print("<option value=\"a\" selected=\"selected\">All Conferences</option>")
else:
	print("<option value=\"a\">All Conferences</option>")

if selected_league is not None and selected_league != "a":
	cursor.callproc("get_conferences_by_league", (selected_league,))
	for result in cursor.fetchall():
		option = "<option value=\"" + str(result[0]) + "\""
		if str(selected_conference) == str(result[0]):
			option += " selected=\"selected\""
		option += ">" + unicode(result[1]).encode("UTF-8") + "</option>"
		print(option)
	while cursor.nextset() is not None: pass

print("""
					</select>
				</span>""")

if selected_entity == "p":
	print("<span class=\"filter_menu\" id=\"span_team\" style=\"display:inline\">")
else:
	print("<span class=\"filter_menu\" id=\"span_team\" style=\"display:none\">")
					
print("""<br />
					Team:
					<select name="t" id="select_team" style="display:inline">""")

if selected_team is None or selected_team == "a":
	print("<option value=\"a\" selected=\"selected\">All Teams</option>")
else:
	print("<option value=\"a\">All Teams</option>")

if selected_conference is not None and selected_conference != "a":
	cursor.callproc("get_teams_by_conference", (selected_conference,))
	for result in cursor.fetchall():
		option = "<option value=\"" + str(result[0]) + "\""
		if str(selected_team) == str(result[0]):
			option += " selected=\"selected\""
		option += ">" + unicode(result[1]).encode("UTF-8") + "</option>"
		print(option)
	while cursor.nextset() is not None: pass

print("""
					</select>
				</span>

				<span class="filter_menu">
					<input type="submit" value="Go" />
				</span>
			</form>

			<!-- Main data display -->
			<table id="rankings">
				<tr id="column_headers">
					<th class="rank_cell">Rank</th>""")

# Column headers
if selected_entity == "t":
	print("<th>Team Name</th><th class=\"stats_cell\">Record</th><th class=\"stats_cell\">Goals<br />For</th><th class=\"stats_cell\">Goals<br />Against</th>")
elif selected_entity == "p":
	print("<th>Player Name</th><th class=\"stats_cell\">Record</th><th class=\"stats_cell\">Goals</th><th class=\"stats_cell\">Assists</th>")
elif selected_entity == "c":
	print("<th>Conference Name</th>")
elif selected_entity == "l":
	print("<th>League Name</th>")

print("<th class=\"stats_cell\">Rating")
print(" <a href=\"about_ratings.html\" onclick=\"return popup(this, 'About Ratings')\">(?)</a>")
print("</th>")
if selected_entity != "p":
	print("<th>")
	print("</th>")
print("</tr>")

if selected_year == "a":
	selected_year = None
if selected_league == "a":
	selected_league = None
if selected_conference == "a":
	selected_conference = None
if selected_team == "a":
	selected_team = None

if selected_entity == "t":
	cursor.callproc("rank_teams", (selected_year, selected_league, selected_conference))
elif selected_entity == "p":
	cursor.callproc("rank_players", (selected_year, selected_league, selected_conference, selected_team))
elif selected_entity == "c":
	cursor.callproc("rank_conferences", (selected_year, selected_league))
elif selected_entity == "l":
	cursor.callproc("rank_leagues", (selected_year,))

rank = 0
for result in cursor.fetchall():
	rank += 1
	print(createHTMLRow(selected_entity, rank, result).encode("UTF-8"))

print("""
				</table>
				<div style="text-align:right;padding-top:5px;"></div>
			</div>
			<div id="page_footer">
				<a href="index.py" class="footer">Home</a>
				<a href="mailto:webmaster@mtubroomballstats.com" class="footer">Contact</a>
				<a href="methodology.html" class="footer">Methodology</a>
			</div>
		</div>
	</body>
</html>
<script>
	lastMenuItem = document.getElementById("rank");
</script>""")

cursor.close()
connection.close()

################################################################################
# END OF FILE                                                                  #
################################################################################
