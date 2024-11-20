Here are the URLs for the Yahoo Fantasy Sports API that are relevant for accessing basketball-specific data. To ensure you're targeting basketball, you'll need the game key (e.g., nba) or specific identifiers for leagues, teams, or players.

1. Game URLs
These URLs focus on metadata and general basketball game information:

Get basketball game metadata:


https://fantasysports.yahooapis.com/fantasy/v2/game/nba
Get basketball game players:


https://fantasysports.yahooapis.com/fantasy/v2/game/nba/players
1. League URLs
These URLs provide league-specific basketball data:

Get details of a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}
Get teams in a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/teams
Get standings for a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/standings
Get scoreboard/matchups for a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/scoreboard
Get available players in a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players
Get settings for a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/settings
3. Team URLs
These URLs provide data about basketball teams:

Get details of a basketball team:


https://fantasysports.yahooapis.com/fantasy/v2/team/{team_key}
Get roster of a basketball team:


https://fantasysports.yahooapis.com/fantasy/v2/team/{team_key}/roster
Get matchup details for a basketball team:


https://fantasysports.yahooapis.com/fantasy/v2/team/{team_key}/matchups
4. Player URLs
These URLs provide data about basketball players:

Get details of a specific basketball player:


https://fantasysports.yahooapis.com/fantasy/v2/player/{player_key}
Get player stats:


https://fantasysports.yahooapis.com/fantasy/v2/player/{player_key}/stats
Search for basketball players:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players;search={player_name}
5. Draft URLs
These URLs provide draft-related basketball data:

Get draft results for a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/draftresults
Get details of a specific draft:


https://fantasysports.yahooapis.com/fantasy/v2/draft/{draft_key}
6. Transaction URLs
These URLs provide basketball league transaction details:

Get all transactions in a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/transactions
Get details of a specific transaction:


https://fantasysports.yahooapis.com/fantasy/v2/transaction/{transaction_key}
7. User URLs
These URLs provide basketball-related data for the authenticated user:

Get all leagues for the authenticated user:


https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=nba/leagues
Get all teams for the authenticated user:


https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games;game_keys=nba/teams
8. Scoreboard and Stats URLs
These URLs provide matchup and statistical data for basketball:

Get basketball league scoreboard:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/scoreboard
Get player or team stats in a basketball league:


https://fantasysports.yahooapis.com/fantasy/v2/league/{league_key}/players/stats
Notes:
Replace placeholders such as {league_key}, {team_key}, {player_key}, {draft_key}, and {transaction_key} with actual values relevant to your data.
To authenticate, use OAuth 2.0 to acquire the necessary tokens for API calls.
Use nba as the game key to specifically target basketball.