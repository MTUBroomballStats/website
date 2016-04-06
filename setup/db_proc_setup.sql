/******************************************************************************
 * db_setup.sql                                                               *
 * Author: Will Weaver                                                        *
 * Sets up the database for the 2016 iteration of the broomball rankings.     *
 ******************************************************************************/
 
/******************************************************************************
 * DATABASE                                                                   *
 ******************************************************************************/
 
USE whweaver_broomball;

/******************************************************************************
 * VIEWS                                                                      *
 ******************************************************************************/
 
DROP VIEW IF EXISTS team_rankings;
CREATE VIEW team_rankings AS
	SELECT	teams.urlnum AS urlnum,
			teams.name AS name,
			SUM(s1.goals > s2.goals) AS wins,
			SUM(s1.goals < s2.goals) AS losses,
			SUM(s1.goals = s2.goals) AS ties,
			SUM(s1.goals) AS goalsFor,
			SUM(s2.goals) AS goalsAgainst,
			teams.rating AS rating
	FROM teams
	JOIN schedules AS s1 ON teams.urlnum = s1.team
	JOIN schedules AS s2 ON s1.game = s2.game
	WHERE s1.team <> s2.team
	GROUP BY teams.urlnum
	ORDER BY teams.rating DESC;

DROP VIEW IF EXISTS player_rankings;
CREATE VIEW player_rankings AS
	SELECT	players.urlnum AS urlnum,
			players.name AS name,
			SUM(s1.goals > s2.goals) AS wins,
			SUM(s1.goals < s2.goals) AS losses,
			SUM(s1.goals = s2.goals) AS ties,
			SUM(appearances.goals) AS goals,
			SUM(appearances.assists) AS assists,
			players.rating AS rating
	FROM players
	JOIN appearances ON players.urlnum = appearances.player
	JOIN schedules AS s1 ON appearances.team = s1.team AND appearances.game = s1.game
	JOIN schedules AS s2 ON s1.game = s2.game
	WHERE s1.team <> s2.team
	GROUP BY players.urlnum
	ORDER BY players.rating DESC;

DROP VIEW IF EXISTS conference_rankings;
CREATE VIEW conference_rankings AS
	SELECT	conferences.id AS id,
			CONCAT(leagues.season, "#", conferences.url) AS url,
			leagues.season AS season,
			conferences.name AS name,
			AVG(teams.rating) AS rating
	FROM conferences
	JOIN leagues ON conferences.league = leagues.id
	JOIN teams ON conferences.id = teams.conference
	GROUP BY conferences.id
	ORDER BY rating DESC;

DROP VIEW IF EXISTS league_rankings;
CREATE VIEW league_rankings AS
	SELECT	leagues.id AS id,
			CONCAT(leagues.season, "#", leagues.url) AS url,
			leagues.season AS season,
			leagues.name AS name,
			AVG(teams.rating) AS rating
	FROM leagues
	JOIN conferences ON leagues.id = conferences.league
	JOIN teams ON conferences.id = teams.conference
	GROUP BY leagues.id
	ORDER BY rating DESC;

DROP VIEW IF EXISTS team_seasons;
CREATE VIEW team_seasons AS
	SELECT	teams.urlnum   AS team,
			leagues.season AS season
	FROM teams
	JOIN conferences ON teams.conference = conferences.id
	JOIN leagues ON conferences.league = leagues.id;

DROP VIEW IF EXISTS first_years;
CREATE VIEW first_years AS
	SELECT  rosters.player AS player,
			MIN(team_seasons.season) AS season
	FROM rosters
	JOIN team_seasons ON rosters.team = team_seasons.team
	GROUP BY rosters.player;

/******************************************************************************
 * STORED PROCEDURES                                                          *
 ******************************************************************************/
 
DELIMITER //

DROP PROCEDURE IF EXISTS update_appearances//
CREATE PROCEDURE update_appearances()
BEGIN
	DELETE FROM appearances
	WHERE NOT EXISTS (
		SELECT schedules.team, schedules.game
		FROM schedules
		WHERE appearances.team = schedules.team
		AND appearances.game = schedules.game
	);
	
	INSERT IGNORE INTO appearances (player, team, game)
	SELECT a1.player, a1.team, a1.game
	FROM (
		SELECT rosters.player AS player, rosters.team AS team, schedules.game AS game
		FROM rosters
		JOIN schedules ON rosters.team = schedules.team
	) AS a1;
END//

DROP PROCEDURE IF EXISTS iterate_player_ratings//
CREATE PROCEDURE iterate_player_ratings(IN p_season INT(4) UNSIGNED)
BEGIN
	DECLARE v_avg FLOAT UNSIGNED;

	/* Calculate the next iteration of ratings */
	DROP TABLE IF EXISTS new_player_ratings;
	CREATE TEMPORARY TABLE new_player_ratings AS
		SELECT	pr1.player AS player,
				pr1.season AS season,
				SUM((ts1.season - fy1.season + 1) / (1 + EXP(-(CAST(s1.goals AS SIGNED)-CAST(s2.goals AS SIGNED)) / 2.3))) /
					SUM((ts1.season - fy1.season + 1) / (pr1.rating + pr2.rating)) AS rating
		FROM player_ratings AS pr1
		JOIN first_years    AS fy1 ON pr1.player = fy1.player
		JOIN rosters 		AS r1  ON pr1.player = r1.player
		JOIN team_seasons   AS ts1 ON r1.team = ts1.team
		JOIN schedules 		AS s1  ON r1.team = s1.team
		JOIN games 				   ON s1.game = games.id
		JOIN schedules 		AS s2  ON games.id = s2.game
		JOIN rosters 		AS r2  ON s2.team = r2.team
		JOIN player_ratings	AS pr2 ON r2.player = pr2.player AND ts1.season = pr2.season
		WHERE s1.team <> s2.team
		AND games.has_played
		AND pr1.rating IS NOT NULL
		AND pr2.rating IS NOT NULL
		AND s1.goals IS NOT NULL
		AND s2.goals IS NOT NULL
		AND pr1.season = p_season
		AND ts1.season <= pr1.season
		GROUP BY pr1.player, pr1.season;

	/* Move the new ratings into the existing ratings table */
	UPDATE player_ratings
	JOIN new_player_ratings AS npr ON player_ratings.player = npr.player AND player_ratings.season = npr.season
	SET player_ratings.rating = npr.rating;

	/* Update players with their latest rating from their last played season */
	UPDATE players
	JOIN (
		SELECT player_ratings.player AS player, MAX(player_ratings.season) AS max_season
		FROM player_ratings
		GROUP BY player_ratings.player
	) AS ms ON players.urlnum = ms.player
	JOIN player_ratings ON ms.player = player_ratings.player AND ms.max_season = player_ratings.season
	SET players.rating = player_ratings.season_adj_rating;
	
	CALL adj_seasons();
	
END//

DROP PROCEDURE IF EXISTS update_team_ratings//
CREATE PROCEDURE update_team_ratings()
BEGIN

	DROP TABLE IF EXISTS team_avg;
	CREATE TEMPORARY TABLE team_avg AS
	SELECT rosters.team AS team, AVG(player_ratings.season_adj_rating) AS avg
	FROM rosters
	JOIN team_seasons ON rosters.team = team_seasons.team
	JOIN player_ratings ON rosters.player = player_ratings.player AND team_seasons.season = player_ratings.season
	GROUP BY rosters.team;

	DROP TABLE IF EXISTS team_stats;
	CREATE TEMPORARY TABLE team_stats AS
	SELECT rosters.team AS team, team_avg.avg AS avg, SQRT(AVG(POW(player_ratings.season_adj_rating - team_avg.avg, 2))) AS stdev
	FROM rosters
	JOIN team_seasons ON rosters.team = team_seasons.team
	JOIN player_ratings ON rosters.player = player_ratings.player AND team_seasons.season = player_ratings.season
	JOIN team_avg ON rosters.team = team_avg.team
	GROUP BY rosters.team;

	UPDATE team_stats
	SET team_stats.stdev = 1
	WHERE team_stats.stdev = 0;

	DROP TABLE IF EXISTS team_z_scores;
	CREATE TEMPORARY TABLE team_z_scores AS
	SELECT rosters.team AS team, rosters.player AS player, ABS(player_ratings.season_adj_rating - team_stats.avg) / team_stats.stdev AS z
	FROM rosters
	JOIN team_seasons ON rosters.team = team_seasons.team
	JOIN player_ratings ON rosters.player = player_ratings.player AND team_seasons.season = player_ratings.season
	JOIN team_stats ON rosters.team = team_stats.team
	WHERE team_stats.stdev > 0;

	UPDATE teams
	INNER JOIN (
		SELECT rosters.team AS team, SUM(player_ratings.season_adj_rating / POW(10, team_z_scores.z)) / SUM(1 / POW(10, team_z_scores.z)) AS rating
		FROM rosters
		JOIN team_seasons ON rosters.team = team_seasons.team
		JOIN player_ratings ON rosters.player = player_ratings.player AND team_seasons.season = player_ratings.season
		JOIN team_z_scores ON rosters.team = team_z_scores.team AND rosters.player = team_z_scores.player
		WHERE player_ratings.season_adj_rating IS NOT NULL
		GROUP BY rosters.team
	) AS ratings ON teams.urlnum = ratings.team
	SET teams.rating = ratings.rating
	WHERE teams.urlnum = ratings.team;
END//

DROP PROCEDURE IF EXISTS iterate_ratings//
CREATE PROCEDURE iterate_ratings(IN p_season INT(4) UNSIGNED)
BEGIN
	CALL iterate_player_ratings(p_season);
	CALL update_team_ratings();
END//

DROP PROCEDURE IF EXISTS play_game//
CREATE PROCEDURE play_game(	IN team1 INT UNSIGNED, IN goals1 INT(3) UNSIGNED,
							IN team2 INT UNSIGNED, IN goals2 INT(3) UNSIGNED)
BEGIN
	DECLARE ct INT;
	DECLARE gameid INT UNSIGNED;
	
	SELECT COUNT(*) INTO ct
	FROM games
	JOIN schedules AS s1 ON games.id = s1.game
	JOIN schedules AS s2 ON games.id = s2.game
	WHERE s1.team = team1
	AND s2.team = team2;
	
	IF ct = 1 THEN
		SELECT games.id INTO gameid
		FROM games
		JOIN schedules AS s1 ON games.id = s1.game
		JOIN schedules AS s2 ON games.id = s2.game
		WHERE s1.team = team1
		AND s2.team = team2;
	
		UPDATE schedules
		SET goals = goals1
		WHERE team = team1
		AND game = gameid;
		
		UPDATE schedules
		SET goals = goals2
		WHERE team = team2
		AND game = gameid;

		UPDATE games
		SET has_played = TRUE
		WHERE id = gameid;
	END IF;
END//

DROP PROCEDURE IF EXISTS get_years//
CREATE PROCEDURE get_years()
BEGIN
	SELECT DISTINCT season
	FROM leagues
	ORDER BY season ASC;
END//

DROP PROCEDURE IF EXISTS get_teams//
CREATE PROCEDURE get_teams(IN p_season INT(4) UNSIGNED)
BEGIN
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
	SELECT id
	FROM games
	WHERE date_time = p_date_time AND location = p_location;
END//

DROP PROCEDURE IF EXISTS get_players//
CREATE PROCEDURE get_players(IN p_team INT UNSIGNED)
BEGIN
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
	IF p_team IS NULL THEN
		SELECT	games.id AS id,
				games.date_time AS date_time,
				games.location AS location,
				s1.team AS team1,
				s1.goals AS goals1,
				s2.team AS team2,
				s2.team AS goals2
		FROM games
		JOIN schedules AS s1 ON games.id = s1.game
		JOIN schedules AS s2 ON games.id = s2.game
		WHERE s1.team <> s2.team;
	ELSE
		SELECT	games.id AS id,
				games.date_time AS date_time,
				games.location AS location,
				s1.team AS team1,
				s1.goals AS goals1,
				s2.team AS team2,
				s2.goals AS goals2
		FROM schedules AS s1
		JOIN games ON s1.game = games.id
		JOIN schedules AS s2 ON games.id = s2.game
		WHERE s1.team = p_team
		AND s1.team <> s2.team;
	END IF;
END//

DROP PROCEDURE IF EXISTS get_appearances//
CREATE PROCEDURE get_appearances(IN p_player INT UNSIGNED)
BEGIN
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
	SELECT a2.player AS player
	FROM appearances AS a1
	JOIN appearances AS a2 ON a1.game = a2.game
	WHERE a1.team <> a2.team
	AND a1.player = p_player;
END//

DROP PROCEDURE IF EXISTS rank_teams//
CREATE PROCEDURE rank_teams(IN p_season INT(4) UNSIGNED,
							IN p_league INT UNSIGNED,
							IN p_conference INT UNSIGNED)
BEGIN
	IF p_conference IS NOT NULL THEN
		SELECT DISTINCT
				team_rankings.urlnum AS urlnum,
				team_rankings.name AS name,
				team_rankings.wins AS wins,
				team_rankings.losses AS losses,
				team_rankings.ties AS ties,
				team_rankings.goalsFor AS goalsFor,
				team_rankings.goalsAgainst AS goalsAgainst,
				team_rankings.rating AS rating
		FROM team_rankings
		JOIN teams ON team_rankings.urlnum = teams.urlnum
		WHERE teams.conference = p_conference;
	ELSE
		IF p_league IS NOT NULL THEN
			SELECT DISTINCT
					team_rankings.urlnum AS urlnum,
					team_rankings.name AS name,
					team_rankings.wins AS wins,
					team_rankings.losses AS losses,
					team_rankings.ties AS ties,
					team_rankings.goalsFor AS goalsFor,
					team_rankings.goalsAgainst AS goalsAgainst,
					team_rankings.rating AS rating
			FROM team_rankings
			JOIN teams ON team_rankings.urlnum = teams.urlnum
			JOIN conferences ON teams.conference = conferences.id
			WHERE conferences.league = p_league;
		ELSE
			IF p_season IS NOT NULL THEN
				SELECT DISTINCT
						team_rankings.urlnum AS urlnum,
						team_rankings.name AS name,
						team_rankings.wins AS wins,
						team_rankings.losses AS losses,
						team_rankings.ties AS ties,
						team_rankings.goalsFor AS goalsFor,
						team_rankings.goalsAgainst AS goalsAgainst,
						team_rankings.rating AS rating
				FROM team_rankings
				JOIN teams ON team_rankings.urlnum = teams.urlnum
				JOIN conferences ON teams.conference = conferences.id
				JOIN leagues ON conferences.league = leagues.id
				WHERE leagues.season = p_season;
			ELSE
				SELECT *
				FROM team_rankings;
			END IF;
		END IF;
	END IF;
END//

DROP PROCEDURE IF EXISTS rank_players//
CREATE PROCEDURE rank_players(	IN p_season INT(4) UNSIGNED,
								IN p_league INT UNSIGNED,
								IN p_conference INT UNSIGNED,
								IN p_team INT UNSIGNED)
BEGIN
	IF p_team IS NOT NULL THEN
		SELECT DISTINCT
				player_rankings.urlnum AS urlnum,
				player_rankings.name AS name,
				player_rankings.wins AS wins,
				player_rankings.losses AS losses,
				player_rankings.ties AS ties,
				player_rankings.goals AS goals,
				player_rankings.assists AS assists,
				player_rankings.rating AS rating
		FROM player_rankings
		JOIN rosters ON player_rankings.urlnum = rosters.player
		WHERE rosters.team = p_team;
	ELSE
		IF p_conference IS NOT NULL THEN
			SELECT DISTINCT
					player_rankings.urlnum AS urlnum,
					player_rankings.name AS name,
					player_rankings.wins AS wins,
					player_rankings.losses AS losses,
					player_rankings.ties AS ties,
					player_rankings.goals AS goals,
					player_rankings.assists AS assists,
					player_rankings.rating AS rating
			FROM player_rankings
			JOIN rosters ON player_rankings.urlnum = rosters.player
			JOIN teams ON rosters.team = teams.urlnum
			WHERE teams.conference = p_conference;
		ELSE
			IF p_league IS NOT NULL THEN
				SELECT DISTINCT
						player_rankings.urlnum AS urlnum,
						player_rankings.name AS name,
						player_rankings.wins AS wins,
						player_rankings.losses AS losses,
						player_rankings.ties AS ties,
						player_rankings.goals AS goals,
						player_rankings.assists AS assists,
						player_rankings.rating AS rating
				FROM player_rankings
				JOIN rosters ON player_rankings.urlnum = rosters.player
				JOIN teams ON rosters.team = teams.urlnum
				JOIN conferences ON teams.conference = conferences.id
				WHERE conferences.league = p_league;
			ELSE
				IF p_season IS NOT NULL THEN
					SELECT DISTINCT
							player_rankings.urlnum AS urlnum,
							player_rankings.name AS name,
							player_rankings.wins AS wins,
							player_rankings.losses AS losses,
							player_rankings.ties AS ties,
							player_rankings.goals AS goals,
							player_rankings.assists AS assists,
							player_rankings.rating AS rating
					FROM player_rankings
					JOIN rosters ON player_rankings.urlnum = rosters.player
					JOIN teams ON rosters.team = teams.urlnum
					JOIN conferences ON teams.conference = conferences.id
					JOIN leagues ON conferences.league = leagues.id
					WHERE leagues.season = p_season;
				ELSE
					SELECT *
					FROM player_rankings;
				END IF;
			END IF;
		END IF;
	END IF;
END//

DROP PROCEDURE IF EXISTS rank_conferences//
CREATE PROCEDURE rank_conferences(	IN p_season INT(4) UNSIGNED,
									IN p_league INT UNSIGNED)
BEGIN
	IF p_league IS NOT NULL THEN
		SELECT DISTINCT
				conference_rankings.id AS id,
				conference_rankings.url AS url,
				conference_rankings.season AS season,
				conference_rankings.name AS name,
				conference_rankings.rating AS rating
		FROM conference_rankings
		JOIN conferences ON conference_rankings.id = conferences.id
		JOIN leagues ON conferences.league = leagues.id
		WHERE leagues.id = p_league;
	ELSE
		IF p_season IS NOT NULL THEN
			SELECT DISTINCT
					conference_rankings.id AS id,
					conference_rankings.url AS url,
					conference_rankings.season AS season,
					conference_rankings.name AS name,
					conference_rankings.rating AS rating
			FROM conference_rankings
			JOIN conferences ON conference_rankings.id = conferences.id
			JOIN leagues ON conferences.league = leagues.id
			WHERE leagues.season = p_season;
		ELSE
			SELECT *
			FROM conference_rankings;
		END IF;
	END IF;
END//

DROP PROCEDURE IF EXISTS rank_leagues//
CREATE PROCEDURE rank_leagues(IN p_season INT(4) UNSIGNED)
BEGIN
	IF p_season IS NOT NULL THEN
		SELECT DISTINCT
				league_rankings.id AS id,
				league_rankings.url AS url,
				league_rankings.season AS season,
				league_rankings.name AS name,
				league_rankings.rating AS rating
		FROM league_rankings
		JOIN leagues ON league_rankings.id = leagues.id
		WHERE leagues.season = p_season;
	ELSE
		SELECT *
		FROM league_rankings;
	END IF;
END//

DROP PROCEDURE IF EXISTS get_years_desc//
CREATE PROCEDURE get_years_desc()
BEGIN
	SELECT DISTINCT season, season
	FROM leagues
	ORDER BY season DESC;
END//

DROP PROCEDURE IF EXISTS get_leagues_by_year//
CREATE PROCEDURE get_leagues_by_year(IN p_season INT(4) UNSIGNED)
BEGIN
	SELECT id, name
	FROM leagues
	WHERE season = p_season;
END//

DROP PROCEDURE IF EXISTS get_conferences_by_league//
CREATE PROCEDURE get_conferences_by_league(IN p_league INT UNSIGNED)
BEGIN
	SELECT id, name
	FROM conferences
	WHERE league = p_league;
END//

DROP PROCEDURE IF EXISTS get_teams_by_conference//
CREATE PROCEDURE get_teams_by_conference(IN p_conference INT UNSIGNED)
BEGIN
	SELECT urlnum, name
	FROM teams
	WHERE conference = p_conference;
END//

DROP PROCEDURE IF EXISTS get_full_team//
CREATE PROCEDURE get_full_team(IN p_team INT UNSIGNED)
BEGIN
	SELECT	teams.urlnum AS urlnum,
			conferences.id AS conference,
			leagues.id AS league,
			leagues.season AS season
	FROM teams
	JOIN conferences ON teams.conference = conferences.id
	JOIN leagues ON conferences.league = leagues.id
	WHERE teams.urlnum = p_team;
END//

DROP PROCEDURE IF EXISTS get_full_conference//
CREATE PROCEDURE get_full_conference(IN p_conference INT UNSIGNED)
BEGIN
	SELECT	conferences.id AS conference,
			leagues.id AS league,
			leagues.season AS season
	FROM conferences
	JOIN leagues ON conferences.league = leagues.id
	WHERE conferences.id = p_conference;
END//

DROP PROCEDURE IF EXISTS get_full_league//
CREATE PROCEDURE get_full_league(IN p_league INT UNSIGNED)
BEGIN
	SELECT	leagues.id AS league,
			leagues.season AS season
	FROM leagues
	WHERE leagues.id = p_league;
END//

DROP PROCEDURE IF EXISTS verify_connectedness//
CREATE PROCEDURE verify_connectedness(IN p_min_season INT(4) UNSIGNED)
BEGIN
	DECLARE v_num_unvisited INT UNSIGNED;
	DECLARE v_num_traversal INT UNSIGNED;
	DECLARE v_cur_player INT UNSIGNED;
	DECLARE v_cur_component INT UNSIGNED;

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
	UPDATE conferences
	SET url = p_url
	WHERE name = p_name AND league = p_league;

	SELECT id
	FROM conferences
	WHERE url = p_url AND name = p_name AND league = p_league;
END//

DROP PROCEDURE IF EXISTS get_pending_games//
CREATE PROCEDURE get_pending_games()
BEGIN
	SELECT	games.date_time AS date_time,
			games.location AS location,
			s1.team AS team1,
			s2.team AS team2
	FROM games
	JOIN schedules AS s1 ON games.id = s1.game
	JOIN schedules AS s2 ON games.id = s2.game
	WHERE s1.team > s2.team
	AND NOT games.has_played
	AND games.date_time < NOW()
	ORDER BY games.date_time ASC;
END//

DROP PROCEDURE IF EXISTS get_roster//
CREATE PROCEDURE get_roster(IN p_team INT UNSIGNED)
BEGIN
	IF p_team IS NULL THEN
		SELECT *
		FROM rosters;
	ELSE
		SELECT rosters.player
		FROM rosters
		WHERE rosters.team = p_team;
	END IF;
END//

DROP PROCEDURE IF EXISTS cancel_game//
CREATE PROCEDURE cancel_game(IN p_game INT UNSIGNED)
BEGIN
	DELETE
	FROM appearances
	WHERE appearances.game = p_game;
	
	DELETE
	FROM schedules
	WHERE schedules.game = p_game;
	
	DELETE
	FROM games
	WHERE games.id = p_game;
END//

DROP PROCEDURE IF EXISTS drop_player//
CREATE PROCEDURE drop_player(IN p_player INT UNSIGNED, IN p_team INT UNSIGNED)
BEGIN
	DELETE
	FROM appearances
	WHERE player = p_player AND team = p_team;
	
	DELETE
	FROM rosters
	WHERE player = p_player AND team = p_team;
END//

DROP PROCEDURE IF EXISTS adj_seasons//
CREATE PROCEDURE adj_seasons()
BEGIN
	UPDATE player_ratings
	JOIN (
		SELECT	(COUNT(season) * SUM(season * rating) - SUM(season) * SUM(rating)) /
					(COUNT(season) * SUM(season * season) - SUM(season) * SUM(season)) AS slope,
				(SUM(rating) * SUM(season * season) - SUM(season) * SUM(season * rating)) /
					(COUNT(season) * SUM(season * season) - SUM(season) * SUM(season)) AS intercept
		FROM (
			SELECT season AS season, LN(AVG(rating)) AS rating
			FROM player_ratings
			GROUP BY season
			HAVING rating IS NOT NULL
		) AS season_avgs
	) AS predictor
	SET player_ratings.season_adj_rating = player_ratings.rating / EXP(predictor.slope * player_ratings.season + predictor.intercept) * 100;
END//

DROP PROCEDURE IF EXISTS setup_player_groups//
CREATE PROCEDURE setup_player_groups()
BEGIN
	
END//

DELIMITER ;

/******************************************************************************
 * TRIGGERS                                                                   *
 ******************************************************************************/

DELIMITER //
 
DROP TRIGGER IF EXISTS player_ratings_archive_trig//
CREATE TRIGGER player_ratings_archive_trig
AFTER UPDATE ON players FOR EACH ROW
BEGIN
	DECLARE last_update TIMESTAMP;
	
	SELECT MAX(date_time) INTO last_update
	FROM player_ratings_archive
	WHERE player = NEW.urlnum;
	
	IF TIMESTAMPDIFF(MINUTE, last_update, NEW.rating_update) >= 30 OR last_update IS NULL THEN
		REPLACE INTO player_ratings_archive (player, rating, date_time)
		VALUES (NEW.urlnum, NEW.rating, NEW.rating_update);
	END IF;
END//

DROP TRIGGER IF EXISTS team_ratings_archive_trig//
CREATE TRIGGER team_ratings_archive_trig
AFTER UPDATE ON teams FOR EACH ROW
BEGIN
	DECLARE last_update TIMESTAMP;
	
	SELECT MAX(date_time) INTO last_update
	FROM team_ratings_archive
	WHERE team = NEW.urlnum;
	
	IF TIMESTAMPDIFF(MINUTE, last_update, NEW.rating_update) >= 30 OR last_update IS NULL THEN
		REPLACE INTO team_ratings_archive (team, rating, date_time)
		VALUES (NEW.urlnum, NEW.rating, NEW.rating_update);
	END IF;
END//

DELIMITER ;

/******************************************************************************
 * FUNCTIONS                                                                  *
 ******************************************************************************/

DELIMITER //
 
DROP FUNCTION IF EXISTS permutations//
CREATE FUNCTION permutations(n INT UNSIGNED, k INT UNSIGNED)
RETURNS DOUBLE UNSIGNED DETERMINISTIC
CONTAINS SQL
BEGIN
	DECLARE i INT UNSIGNED;
	DECLARE p INT UNSIGNED;
	
	SET i = n;
	SET p = 1;
	WHILE i > n - k DO
		SET p = p * i;
		SET i = i - 1;
	END WHILE;
	
	RETURN p;
END//

DROP FUNCTION IF EXISTS prob_group_play//
CREATE FUNCTION prob_group_play(n INT UNSIGNED, i INT UNSIGNED, g INT UNSIGNED)
RETURNS DOUBLE UNSIGNED DETERMINISTIC
NO SQL
BEGIN
	RETURN permutations(i, g)/permutations(n, g);
END//

DROP FUNCTION IF EXISTS prob_group_on_ice//
CREATE FUNCTION prob_group_on_ice(n INT UNSIGNED, g INT UNSIGNED)
RETURNS DOUBLE UNSIGNED DETERMINISTIC
NO SQL
BEGIN
	RETURN prob_group_play(n, 6, g);
END//

DELIMITER ;
 
/******************************************************************************
 * END OF FILE                                                                *
 ******************************************************************************/