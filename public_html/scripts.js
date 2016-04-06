/******************************************************************************
 * scripts.js                                                                 *
 * Author: Will Weaver                                                        *
 * Contains scripts for mtubroomballstats/index.py                            *
 ******************************************************************************/

function change_entity() {

	// Get the new entity
	var entity_select = document.getElementById("select_entity");
	var new_entity = entity_select.options[entity_select.selectedIndex].value;

	// Adjust which filters are available based on the entity
	switch (new_entity) {
		case "t":
			document.getElementById("span_league").style.display = "inline";
			document.getElementById("span_conference").style.display = "inline";
			document.getElementById("span_team").style.display = "none";
			break;
		case "p":
			document.getElementById("span_league").style.display = "inline";
			document.getElementById("span_conference").style.display = "inline";
			document.getElementById("span_team").style.display = "inline";
			break;
		case "c":
			document.getElementById("span_league").style.display = "inline";
			document.getElementById("span_conference").style.display = "none";
			document.getElementById("span_team").style.display = "none";
			break;
		case "l":
			document.getElementById("span_league").style.display = "none";
			document.getElementById("span_conference").style.display = "none";
			document.getElementById("span_team").style.display = "none";
			break;
	}
}

function change_year() {

	// Get the new year
	var year_select = document.getElementById("select_year");
	var new_year = year_select.options[year_select.selectedIndex].value;

	// Get the league dropdown
	var league_select = document.getElementById("select_league");

	// Clear old leagues
	clear_options(league_select);
	var new_league_option = document.createElement("option");
	new_league_option.value = "a";
	new_league_option.text = "All Leagues";
	league_select.add(new_league_option);

	// Propagate changes
	change_league();
	change_conference();

	// Set up the request for new leagues
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {

			// Get the new leagues from the new year
			var new_leagues = JSON.parse(xmlhttp.responseText);

			// Add the new leagues to the dropdown
			for (var league_id in new_leagues) {
				var new_league_option = document.createElement("option");
				new_league_option.value = league_id;
				new_league_option.text = new_leagues[league_id];
				league_select.add(new_league_option);
			}
		}
	};

	// Make the request
	if (new_year == "a")
		xmlhttp.open("GET", "db/get_leagues_by_year.py", true);
	else
		xmlhttp.open("GET", "db/get_leagues_by_year.py?y=" + new_year, true);
	xmlhttp.send();
}

function change_league() {

	// Get the new league
	var league_select = document.getElementById("select_league");
	var new_league = league_select.options[league_select.selectedIndex].value;

	// Get the conference dropdown
	var conference_select = document.getElementById("select_conference");

	// Clear old conferences
	clear_options(conference_select);
	var new_conference_option = document.createElement("option");
	new_conference_option.value = "a";
	new_conference_option.text = "All Conferences";
	conference_select.add(new_conference_option);

	// Propagate changes
	change_conference();

	// Set up the request for new conferences
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {

			// Get the new conferences from the new league
			var new_conferences = JSON.parse(xmlhttp.responseText);

			// Add the new conference to the dropdown
			for (var conference_id in new_conferences) {
				var new_conference_option = document.createElement("option");
				new_conference_option.value = conference_id;
				new_conference_option.text = new_conferences[conference_id];
				conference_select.add(new_conference_option);
			}
		}
	};

	// Make the request
	if (new_league == "a")
		xmlhttp.open("GET", "db/get_conferences_by_league.py", true);
	else
		xmlhttp.open("GET", "db/get_conferences_by_league.py?l=" + new_league, true);
	xmlhttp.send();
}

function change_conference() {
	// Get the new conference
	var conference_select = document.getElementById("select_conference");
	var new_conference = conference_select.options[conference_select.selectedIndex].value;

	// Get the team dropdown
	var team_select = document.getElementById("select_team");

	// Clear old teams
	clear_options(team_select);
	var new_team_option = document.createElement("option");
	new_team_option.value = "a";
	new_team_option.text = "All Teams";
	team_select.add(new_team_option);

	// Set up the request for new teams
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {

			// Get the new teams from the new conference
			var new_teams = JSON.parse(xmlhttp.responseText);

			// Add the new team to the dropdown
			for (var team_id in new_teams) {
				var new_team_option = document.createElement("option");
				new_team_option.value = team_id;
				new_team_option.text = new_teams[team_id];
				team_select.add(new_team_option);
			}
		}
	};

	// Make the request
	if (new_conference == "a")
		xmlhttp.open("GET", "db/get_teams_by_conference.py", true);
	else
		xmlhttp.open("GET", "db/get_teams_by_conference.py?c=" + new_conference, true);
	xmlhttp.send();
}

function clear_options(select_box) {
    for(var i=select_box.options.length-1;i>=0;i--)
        select_box.remove(i);
}

function popup(mylink, windowname) {
	if (! window.focus)
		return true;

	var href;
	if (typeof(mylink) == 'string')
		href=mylink;
	else
		href=mylink.href; window.open(href, windowname, 'width=500,height=350,scrollbars=yes');

	return false;
}

/******************************************************************************
 * END OF FILE                                                                *
 ******************************************************************************/