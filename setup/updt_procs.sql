/******************************************************************************
 * updt_procs.sql                                                             *
 * Author: Will Weaver                                                        *
 * Sets up the internal database stored procedures.                           *
 ******************************************************************************/
 
/******************************************************************************
 * DATABASE                                                                   *
 ******************************************************************************/
 
USE whweaver_bbupdt;

/******************************************************************************
 * STORED PROCEDURES                                                          *
 ******************************************************************************/
 
DELIMITER //

DROP PROCEDURE IF EXISTS iterate_player_ratings//
CREATE PROCEDURE iterate_player_ratings()
BEGIN
	USE whweaver_bbupdt;

	/* Implements equation Ki = Vi / SUM(Nij/(Ki+Kj)) */
	UPDATE players
	JOIN (
		SELECT	p1.urlnum AS player,
				(SUM(s1.goals > s2.goals) + SUM(s1.goals = s2.goals)/2) /
					SUM(1 / (p1.rating + p2.rating)) AS rating
		FROM players AS p1
		JOIN rosters AS r1 ON p1.urlnum = r1.player
		JOIN schedules AS s1 ON r1.team = s1.team
		JOIN games ON s1.game = games.id
		JOIN schedules AS s2 ON games.id = s2.game
		JOIN rosters AS r2 ON s2.team = r2.team
		JOIN players AS p2 ON r2.player = p2.urlnum
		WHERE s1.team <> s2.team AND games.has_played
		AND p1.rating IS NOT NULL
		AND p2.rating IS NOT NULL
		AND s1.goals IS NOT NULL
		AND s2.goals IS NOT NULL
		GROUP BY p1.urlnum
	) AS ratings ON players.urlnum = ratings.player
	SET players.rating = ratings.rating
	WHERE players.urlnum = ratings.player;
END//

DROP PROCEDURE IF EXISTS update_team_ratings//
CREATE PROCEDURE update_team_ratings()
BEGIN
	USE whweaver_bbupdt;

	DROP TABLE IF EXISTS team_avg;
	CREATE TEMPORARY TABLE team_avg AS
	SELECT rosters.team AS team, AVG(players.rating) AS avg
	FROM rosters
	JOIN players ON rosters.player = players.urlnum
	GROUP BY rosters.team;

	DROP TABLE IF EXISTS team_stats;
	CREATE TEMPORARY TABLE team_stats AS
	SELECT rosters.team AS team, team_avg.avg AS avg, SQRT(AVG(POW(players.rating - team_avg.avg, 2))) AS stdev
	FROM rosters
	JOIN players ON rosters.player = players.urlnum
	JOIN team_avg ON rosters.team = team_avg.team
	GROUP BY rosters.team;

	UPDATE team_stats
	SET team_stats.stdev = 1
	WHERE team_stats.stdev = 0;

	DROP TABLE IF EXISTS team_z_scores;
	CREATE TEMPORARY TABLE team_z_scores AS
	SELECT rosters.team AS team, rosters.player AS player, ABS(players.rating - team_stats.avg) / team_stats.stdev AS z
	FROM rosters
	JOIN players ON rosters.player = players.urlnum
	JOIN team_stats ON rosters.team = team_stats.team
	WHERE team_stats.stdev > 0;

	UPDATE teams
	JOIN (
		SELECT rosters.team AS team, SUM(players.rating / POW(10, team_z_scores.z)) / SUM(1 / POW(10, team_z_scores.z)) AS rating
		FROM rosters
		JOIN players ON rosters.player = players.urlnum
		JOIN team_z_scores ON rosters.team = team_z_scores.team AND rosters.player = team_z_scores.player
		WHERE players.rating IS NOT NULL
		GROUP BY rosters.team
	) AS ratings ON teams.urlnum = ratings.team
	SET teams.rating = ratings.rating
	WHERE teams.urlnum = ratings.team;
END//

DROP PROCEDURE IF EXISTS iterate_ratings//
CREATE PROCEDURE iterate_ratings()
BEGIN
	USE whweaver_bbupdt;
	CALL iterate_player_ratings();
	CALL update_team_ratings();
END//

DROP PROCEDURE IF EXISTS play_game//
CREATE PROCEDURE play_game(	IN team1 INT UNSIGNED, IN goals1 INT(3) UNSIGNED,
							IN team2 INT UNSIGNED, IN goals2 INT(3) UNSIGNED)
BEGIN
	DECLARE ct INT;
	USE whweaver_bbupdt;
	
	SELECT COUNT(*) INTO ct
	FROM games
	JOIN schedules AS s1 ON games.id = s1.gameid
	JOIN schedules AS s2 ON games.id = s2.gameid
	WHERE s1.team = team1
	AND s2.team = team2;
	
	IF ct = 1 THEN
		UPDATE schedules
		SET goals = goals1
		WHERE team = team1;
		
		UPDATE schedules
		SET goals = goals2
		WHERE team = team2;

		UPDATE games
		JOIN schedules AS s1 ON games.id = s1.game
		JOIN schedules AS s2 ON games.id = s2.game
		SET has_played = TRUE
		WHERE s1.team = team1
		AND s2.team = team2;
	END IF;
END//

DROP PROCEDURE IF EXISTS get_years//
CREATE PROCEDURE get_years()
BEGIN
	USE whweaver_bbupdt;
	SELECT DISTINCT season
	FROM leagues
	ORDER BY season ASC;
END//

DROP PROCEDURE IF EXISTS get_teams//
CREATE PROCEDURE get_teams(IN p_season INT(4) UNSIGNED)
BEGIN
	USE whweaver_bbupdt;
	IF p_season IS NULL THEN
		SELECT urlnum
		FROM teams
		ORDER BY urlnum ASC;
	ELSE
		SELECT teams.urlnum
		FROM teams
		JOIN conferences ON teams.conference = conferences.id
		JOIN leagues ON conferences.league = leagues.id
		WHERE leagues.season = p_season
		ORDER BY urlnum ASC;
	END IF;
END//

DROP PROCEDURE IF EXISTS insert_league//
CREATE PROCEDURE insert_league(IN p_url VARCHAR(16), IN p_name VARCHAR(63), IN p_season INT(4) UNSIGNED)
BEGIN
	DECLARE ct INT;
	USE whweaver_bbupdt;
	
	SELECT COUNT(*) INTO ct
	FROM leagues
	WHERE url = p_url AND name = p_name AND season = p_season;
	
	IF ct = 0 THEN
		INSERT INTO leagues (url, name, season)
		VALUES (p_url, p_name, p_season);
	END IF;
	
	SELECT id
	FROM leagues
	WHERE url = p_url AND name = p_name AND season = p_season;
END//

DROP PROCEDURE IF EXISTS insert_conference//
CREATE PROCEDURE insert_conference(IN p_url VARCHAR(16), IN p_name VARCHAR(63), IN p_league INT UNSIGNED)
BEGIN
	DECLARE ct INT;
	USE whweaver_bbupdt;
	
	SELECT COUNT(*) INTO ct
	FROM conferences
	WHERE url = p_url AND name = p_name AND league = p_league;
	
	IF ct = 0 THEN
		INSERT INTO conferences (url, name, league)
		VALUES (p_url, p_name, p_league);
	END IF;
	
	SELECT id
	FROM conferences
	WHERE url = p_url AND name = p_name AND league = p_league;
END//

DROP PROCEDURE IF EXISTS insert_team//
CREATE PROCEDURE insert_team(IN p_urlnum INT UNSIGNED, IN p_name VARCHAR(255), IN p_conference INT UNSIGNED)
BEGIN
	DECLARE ct INT;
	USE whweaver_bbupdt;
	
	SELECT COUNT(*) INTO ct
	FROM teams
	WHERE urlnum = p_urlnum;
	
	IF ct = 0 THEN
		INSERT INTO teams (urlnum, name, conference)
		VALUES (p_urlnum, p_name, p_conference);
	END IF;
	
	SELECT p_urlnum;
END//

DROP PROCEDURE IF EXISTS insert_game//
CREATE PROCEDURE insert_game(	IN p_team1 INT UNSIGNED,
								IN p_team2 INT UNSIGNED,
								IN p_date_time DATETIME,
								IN p_location VARCHAR(31),
								IN goals1 INT(3) UNSIGNED,
								IN goals2 INT(3) UNSIGNED)
BEGIN
	DECLARE ct INT;
	DECLARE v_game INT UNSIGNED;
	USE whweaver_bbupdt;

	SELECT COUNT(*) INTO ct
	FROM teams
	WHERE urlnum = p_team1 OR urlnum = p_team2;

	IF ct = 2 THEN
	
		SELECT COUNT(*) INTO ct
		FROM games
		WHERE date_time = p_date_time AND location = p_location;
		
		IF ct = 0 THEN
			INSERT INTO games (date_time, location)
			VALUES (p_date_time, p_location);
		END IF;
		
		SELECT id INTO v_game
		FROM games
		WHERE date_time = p_date_time AND location = p_location;
		
		SELECT COUNT(*) INTO ct
		FROM schedules
		WHERE game = v_game AND team = p_team1;
		
		IF ct = 0 THEN
			INSERT INTO schedules (game, team, goals)
			VALUES (v_game, p_team1, goals1);
		ELSE
			UPDATE schedules
			SET goals = goals1
			WHERE game = v_game AND team = p_team1;
		END IF;
		
		SELECT COUNT(*) INTO ct
		FROM schedules
		WHERE game = v_game AND team = p_team2;
		
		IF ct = 0 THEN
			INSERT INTO schedules (game, team, goals)
			VALUES (v_game, p_team2, goals2);
		ELSE
			UPDATE schedules
			SET goals = goals2
			WHERE game = v_game AND team = p_team2;
		END IF;
		
		SELECT v_game;
	ELSE
		SELECT NULL;
	END IF;
END//

DROP PROCEDURE IF EXISTS insert_player//
CREATE PROCEDURE insert_player(	IN p_urlnum INT UNSIGNED,
								IN p_name VARCHAR(255))
BEGIN
	DECLARE ct INT;
	USE whweaver_bbupdt;
	
	SELECT COUNT(*) INTO ct
	FROM players
	WHERE urlnum = p_urlnum;
	
	IF ct = 0 THEN
		INSERT INTO players (urlnum, name)
		VALUES (p_urlnum, p_name);
	END IF;
END//

DROP PROCEDURE IF EXISTS update_player//
CREATE PROCEDURE update_player(	IN p_urlnum INT UNSIGNED,
								IN p_username VARCHAR(31),
								IN p_name VARCHAR(255))
BEGIN
	USE whweaver_bbupdt;
	UPDATE players
	SET username = p_username, name = p_name
	WHERE urlnum = p_urlnum;
END//

DROP PROCEDURE IF EXISTS add_player_to_team//
CREATE PROCEDURE add_player_to_team(IN p_player INT UNSIGNED,
									IN p_team INT UNSIGNED,
									IN p_saves INT(4) UNSIGNED,
									IN p_goalie_mins INT(4) UNSIGNED,
									IN p_goals_against INT(3) UNSIGNED)
BEGIN
	DECLARE ct INT;
	USE whweaver_bbupdt;
	
	SELECT COUNT(*) INTO ct
	FROM rosters
	WHERE player = p_player AND team = p_team;
	
	IF ct = 0 THEN
		INSERT INTO rosters (player, team, saves, goalie_mins, goals_against)
		VALUES (p_player, p_team, p_saves, p_goalie_mins, p_goals_against);
	END IF;
END//

DROP PROCEDURE IF EXISTS add_player_to_game//
CREATE PROCEDURE add_player_to_game(IN p_game INT UNSIGNED,
									IN p_player INT UNSIGNED,
									IN p_team INT UNSIGNED,
									IN p_goals INT(3) UNSIGNED,
									IN p_assists INT(3) UNSIGNED,
									IN p_pen_mins INT(2) UNSIGNED)
BEGIN
	DECLARE ct INT;
	USE whweaver_bbupdt;
	
	SELECT COUNT(*) INTO ct
	FROM appearances
	WHERE game = p_game AND player = p_player AND team = p_team;
	
	IF ct = 0 THEN
		INSERT INTO appearances (game, player, team, goals, assists, pen_mins)
		VALUES (p_game, p_player, p_team, p_goals, p_assists, p_pen_mins);
	END IF;
END//

DROP PROCEDURE IF EXISTS get_game_id//
CREATE PROCEDURE get_game_id(IN p_date_time DATETIME, IN p_location VARCHAR(31))
BEGIN
	USE whweaver_bbupdt;
	SELECT id
	FROM games
	WHERE date_time = p_date_time AND location = p_location;
END//

DROP PROCEDURE IF EXISTS get_players//
CREATE PROCEDURE get_players(IN p_team INT UNSIGNED)
BEGIN
	USE whweaver_bbupdt;
	IF p_team IS NULL THEN
		SELECT urlnum
		FROM players;
	ELSE
		SELECT player
		FROM rosters
		WHERE team = p_team;
	END IF;
END//

DROP PROCEDURE IF EXISTS get_schedule//
CREATE PROCEDURE get_schedule(IN p_team INT UNSIGNED)
BEGIN
	USE whweaver_bbupdt;
	IF p_team IS NULL THEN
		SELECT id
		FROM games;
	ELSE
		SELECT game
		FROM schedules
		WHERE team = p_team;
	END IF;
END//

DROP PROCEDURE IF EXISTS get_appearances//
CREATE PROCEDURE get_appearances(IN p_player INT UNSIGNED)
BEGIN
	USE whweaver_bbupdt;
	IF p_player IS NULL THEN
		SELECT game
		FROM appearances;
	ELSE
		SELECT game
		FROM appearances
		WHERE player = p_player;
	END IF;
END//

DROP PROCEDURE IF EXISTS get_players_played//
CREATE PROCEDURE get_players_played(IN p_player INT UNSIGNED)
BEGIN
	USE whweaver_bbupdt;
	SELECT a2.player AS player
	FROM appearances AS a1
	JOIN appearances AS a2 ON a1.game = a2.game
	WHERE a1.team <> a2.team
	AND a1.player = p_player;
END//

DROP PROCEDURE IF EXISTS verify_connectedness//
CREATE PROCEDURE verify_connectedness(IN p_min_season INT(4) UNSIGNED)
BEGIN
	DECLARE v_num_unvisited INT UNSIGNED;
	DECLARE v_num_traversal INT UNSIGNED;
	DECLARE v_cur_player INT UNSIGNED;
	DECLARE v_cur_component INT UNSIGNED;
	USE whweaver_bbupdt;

	DROP TABLE IF EXISTS unvisited;
	CREATE TEMPORARY TABLE unvisited (
		player INT UNSIGNED,
		PRIMARY KEY (player),
		FOREIGN KEY (player) REFERENCES players(urlnum)
	);

	DROP TABLE IF EXISTS components;
	CREATE TABLE components (
		id INT UNSIGNED AUTO_INCREMENT,
		PRIMARY KEY(id)
	);

	DROP TABLE IF EXISTS subgraphs;
	CREATE TABLE subgraphs (
		component INT UNSIGNED,
		player INT UNSIGNED,
		PRIMARY KEY (component, player),
		FOREIGN KEY (component) REFERENCES components(id),
		FOREIGN KEY (player) REFERENCES players(urlnum)
	);

	DROP TABLE IF EXISTS traversal;
	CREATE TEMPORARY TABLE traversal (
		player INT UNSIGNED,
		PRIMARY KEY (player),
		FOREIGN KEY (player) REFERENCES players(urlnum)
	);

	IF p_min_season IS NULL THEN
		INSERT INTO unvisited
		SELECT urlnum
		FROM players;
	ELSE
		INSERT INTO unvisited
		SELECT players.urlnum
		FROM players
		JOIN rosters ON players.urlnum = rosters.player
		JOIN teams ON rosters.team = teams.urlnum
		JOIN conferences ON teams.conference = conferences.id
		JOIN leagues ON conferences.league = leagues.id
		GROUP BY players.urlnum
		HAVING MAX(leagues.season) >= p_min_season;
	END IF;

	SELECT COUNT(*) INTO v_num_unvisited
	FROM unvisited;

	WHILE (v_num_unvisited > 0) DO

		INSERT INTO components ()
		VALUES ();

		SELECT LAST_INSERT_ID() INTO v_cur_component;

		INSERT INTO traversal (player)
		SELECT player
		FROM unvisited
		LIMIT 1;

		SELECT COUNT(*) INTO v_num_traversal
		FROM traversal;

		WHILE (v_num_traversal > 0) DO
			SELECT player INTO v_cur_player
			FROM traversal
			LIMIT 1;

			DELETE FROM traversal
			WHERE player = v_cur_player;

			REPLACE INTO traversal (player)
			SELECT a2.player AS player
			FROM appearances AS a1
			JOIN appearances AS a2 ON a1.game = a2.game
			INNER JOIN unvisited ON a2.player = unvisited.player
			WHERE a1.team <> a2.team
			AND a1.player <> a2.player
			AND a1.player = v_cur_player;

			DELETE FROM unvisited
			WHERE player = v_cur_player;

			INSERT INTO subgraphs (component, player)
			VALUES (v_cur_component, v_cur_player);

			SELECT COUNT(*) INTO v_num_traversal
			FROM traversal;

		END WHILE;

		SELECT COUNT(*) INTO v_num_unvisited
		FROM unvisited;

	END WHILE;

END//

DROP PROCEDURE IF EXISTS add_league_url//
CREATE PROCEDURE add_league_url(IN p_url VARCHAR(16), IN p_name VARCHAR(63), IN p_season INT(4) UNSIGNED)
BEGIN
	USE whweaver_bbupdt;
	UPDATE leagues
	SET url = p_url
	WHERE name = p_name AND season = p_season;

	SELECT id
	FROM leagues
	WHERE url = p_url AND name = p_name AND season = p_season;
END//

DROP PROCEDURE IF EXISTS add_conference_url//
CREATE PROCEDURE add_conference_url(IN p_url VARCHAR(16), IN p_name VARCHAR(63), IN p_league INT UNSIGNED)
BEGIN
	USE whweaver_bbupdt;
	UPDATE conferences
	SET url = p_url
	WHERE name = p_name AND league = p_league;

	SELECT id
	FROM conferences
	WHERE url = p_url AND name = p_name AND league = p_league;
END//

DELIMITER ;
 
/******************************************************************************
 * END OF FILE                                                                *
 ******************************************************************************/