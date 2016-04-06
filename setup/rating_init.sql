UPDATE players
JOIN (
	SELECT player_ratings_archive.player, player_ratings_archive.rating
	FROM player_ratings_archive
	JOIN (
		SELECT player AS player, MAX(date_time) AS date_time
		FROM player_ratings_archive
		GROUP BY player
	) AS recent ON player_ratings_archive.player = recent.player
	WHERE player_ratings_archive.date_time = recent.date_time
) AS rt ON players.urlnum = rt.player
SET players.rating = rt.rating;