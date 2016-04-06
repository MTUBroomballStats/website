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
 * TABLES                                                                     *
 ******************************************************************************/

DROP TABLE IF EXISTS appearances;
DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS rosters;
DROP TABLE IF EXISTS player_group_rosters;
DROP TABLE IF EXISTS player_group_ratings;
DROP TABLE IF EXISTS player_groups;
DROP TABLE IF EXISTS player_ratings;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS conferences;
DROP TABLE IF EXISTS leagues;
DROP TABLE IF EXISTS player_ratings_archive;
DROP TABLE IF EXISTS team_ratings_archive;

CREATE TABLE leagues (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	name VARCHAR(63),
	season INT(4) UNSIGNED,
	PRIMARY KEY (id)
) ENGINE = INNODB;
 
CREATE TABLE conferences (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	name VARCHAR(127),
	league INT(6) UNSIGNED NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY (league) REFERENCES leagues(id) ON UPDATE RESTRICT
) ENGINE = INNODB;
 
CREATE TABLE teams (
	urlnum INT UNSIGNED NOT NULL,
	name VARCHAR(255),
	conference INT(6) UNSIGNED NOT NULL,
	rating FLOAT UNSIGNED,
	rating_update TIMESTAMP DEFAULT 0 ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (urlnum),
	FOREIGN KEY (conference) REFERENCES conferences(id) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE players (
	urlnum INT UNSIGNED NOT NULL,
	username VARCHAR(31),
	name VARCHAR(255),
	rating FLOAT UNSIGNED,
	rating_update TIMESTAMP DEFAULT 0 ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (urlnum)
) ENGINE = INNODB;

CREATE TABLE rosters (
	team INT UNSIGNED NOT NULL,
	player INT UNSIGNED NOT NULL,
	saves INT(4) UNSIGNED,
	goalie_mins INT(4) UNSIGNED,
	goals_against INT(3) UNSIGNED,
	PRIMARY KEY (team, player),
	FOREIGN KEY (team) REFERENCES teams(urlnum) ON UPDATE RESTRICT,
	FOREIGN KEY (player) REFERENCES players(urlnum) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE games (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	date_time DATETIME,
	location VARCHAR(31),
	has_played BOOLEAN,
	PRIMARY KEY (id)
) ENGINE = INNODB;

CREATE TABLE schedules (
	game INT UNSIGNED NOT NULL,
	team INT UNSIGNED NOT NULL,
	goals INT(3) UNSIGNED,
	PRIMARY KEY (game, team),
	FOREIGN KEY (game) REFERENCES games(id) ON UPDATE RESTRICT,
	FOREIGN KEY (team) REFERENCES teams(urlnum) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE appearances (
	game INT UNSIGNED NOT NULL,
	player INT UNSIGNED NOT NULL,
	team INT UNSIGNED NOT NULL,
	goals INT(3) UNSIGNED,
	assists INT(3) UNSIGNED,
	pen_mins INT(2) UNSIGNED,
	PRIMARY KEY (game, player, team),
	FOREIGN KEY (game) REFERENCES games(id) ON UPDATE RESTRICT,
	FOREIGN KEY (player) REFERENCES players(urlnum) ON UPDATE RESTRICT,
	FOREIGN KEY (team) REFERENCES teams(urlnum) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE player_ratings_archive (
	player INT UNSIGNED NOT NULL,
	rating FLOAT UNSIGNED,
	date_time TIMESTAMP,
	PRIMARY KEY (player, rating),
	FOREIGN KEY (player) REFERENCES players(urlnum) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE team_ratings_archive (
	team INT UNSIGNED NOT NULL,
	rating FLOAT UNSIGNED,
	date_time TIMESTAMP,
	PRIMARY KEY (team, rating),
	FOREIGN KEY (team) REFERENCES teams(urlnum) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE player_ratings (
	player INT UNSIGNED NOT NULL,
	season INT(4) UNSIGNED NOT NULL,
	rating FLOAT UNSIGNED,
	season_adj_rating FLOAT UNSIGNED,
	time_updated TIMESTAMP DEFAULT 0 ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (player, season),
	FOREIGN KEY (player) REFERENCES players(urlnum) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE player_groups (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	PRIMARY KEY (id)
) ENGINE = INNODB;

CREATE TABLE player_group_rosters (
	player_group INT UNSIGNED NOT NULL,
	player INT UNSIGNED NOT NULL,
	PRIMARY KEY (player_group, player),
	FOREIGN KEY (player_group) REFERENCES player_groups(id) ON UPDATE RESTRICT,
	FOREIGN KEY (player) REFERENCES players(urlnum) ON UPDATE RESTRICT
) ENGINE = INNODB;

CREATE TABLE player_group_ratings (
	player_group INT UNSIGNED NOT NULL,
	season INT(4) UNSIGNED NOT NULL,
	rating FLOAT UNSIGNED,
	season_adj_rating FLOAT UNSIGNED,
	time_updated TIMESTAMP DEFAULT 0 ON UPDATE CURRENT TIMESTAMP,
	PRIMARY KEY (player_group, season),
	FOREIGN KEY (player_group) REFERENCES player_groups(id) ON UPDATE RESTRICT
) ENGINE = INNODB;

/******************************************************************************
 * END OF FILE                                                                *
 ******************************************************************************/