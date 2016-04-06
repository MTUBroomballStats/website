/******************************************************************************
 * xpsd_procs.sql                                                             *
 * Author: Will Weaver                                                        *
 * Sets up the client-exposed database stored procedures.                     *
 ******************************************************************************/
 
/******************************************************************************
 * DATABASE                                                                   *
 ******************************************************************************/
 
USE whweaver_bbxpsd;

/******************************************************************************
 * VIEWS                                                                      *
 ******************************************************************************/

DROP VIEW IF EXISTS team_rankings;
DROP VIEW IF EXISTS player_rankings;
DROP VIEW IF EXISTS conference_rankings;
DROP VIEW IF EXISTS league_rankings;

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

/******************************************************************************
 * STORED PROCEDURES                                                          *
 ******************************************************************************/
 
DELIMITER //

DROP PROCEDURE IF EXISTS rank_teams//
CREATE PROCEDURE rank_teams(IN p_season INT(4) UNSIGNED,
							IN p_league INT UNSIGNED,
							IN p_conference INT UNSIGNED)
BEGIN
	USE whweaver_bbxpsd;
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
	USE whweaver_bbxpsd;
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
	USE whweaver_bbxpsd;
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
	USE whweaver_bbxpsd;
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
	USE whweaver_bbxpsd;
	SELECT DISTINCT season, season
	FROM leagues
	ORDER BY season DESC;
END//

DROP PROCEDURE IF EXISTS get_leagues_by_year//
CREATE PROCEDURE get_leagues_by_year(IN p_season INT(4) UNSIGNED)
BEGIN
	USE whweaver_bbxpsd;
	SELECT id, name
	FROM leagues
	WHERE season = p_season;
END//

DROP PROCEDURE IF EXISTS get_conferences_by_league//
CREATE PROCEDURE get_conferences_by_league(IN p_league INT UNSIGNED)
BEGIN
	USE whweaver_bbxpsd;
	SELECT id, name
	FROM conferences
	WHERE league = p_league;
END//

DROP PROCEDURE IF EXISTS get_teams_by_conference//
CREATE PROCEDURE get_teams_by_conference(IN p_conference INT UNSIGNED)
BEGIN
	USE whweaver_bbxpsd;
	SELECT urlnum, name
	FROM teams
	WHERE conference = p_conference;
END//

DROP PROCEDURE IF EXISTS get_full_team//
CREATE PROCEDURE get_full_team(IN p_team INT UNSIGNED)
BEGIN
	USE whweaver_bbxpsd;
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
	USE whweaver_bbxpsd;
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
	USE whweaver_bbxpsd;
	SELECT	leagues.id AS league,
			leagues.season AS season
	FROM leagues
	WHERE leagues.id = p_league;
END//

DELIMITER ;
 
/******************************************************************************
 * END OF FILE                                                                *
 ******************************************************************************/