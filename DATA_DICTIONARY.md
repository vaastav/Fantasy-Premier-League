# Data Dictionary

This document provides detailed explanations for all variables/columns found in the Fantasy Premier League dataset.

---

## Table of Contents

1. [players_raw.csv](#players_rawcsv)
2. [cleaned_players.csv](#cleaned_playerscsv)
3. [Gameweek Files (gw*.csv)](#gameweek-files-gwcsv)
4. [fixtures.csv](#fixturescsv)
5. [teams.csv](#teamscsv)
6. [Player History Files](#player-history-files)
7. [Understat Data](#understat-data)

---

## players_raw.csv

The main player data file containing all available statistics from the FPL API.

### Player Identification

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Unique FPL player identifier |
| `code` | int | Internal FPL player code |
| `opta_code` | int | Opta sports data provider code |
| `first_name` | str | Player's first name |
| `second_name` | str | Player's surname |
| `web_name` | str | Display name used on FPL website |
| `photo` | str | Player photo filename |
| `birth_date` | str | Player's date of birth |
| `region` | int | Player's region/nationality code |

### Team Information

| Column | Type | Description |
|--------|------|-------------|
| `team` | int | Team ID (1-20) |
| `team_code` | int | Internal team code |
| `team_join_date` | str | Date player joined current team |
| `squad_number` | int | Player's squad number (null if not assigned) |

### Position & Status

| Column | Type | Description |
|--------|------|-------------|
| `element_type` | int | Position: 1=GK, 2=DEF, 3=MID, 4=FWD |
| `status` | str | Availability: a=available, d=doubtful, i=injured, s=suspended, u=unavailable, n=not in squad |
| `news` | str | Latest news/injury update about the player |
| `news_added` | str | Timestamp when news was added |
| `chance_of_playing_this_round` | int | Probability (0-100) of playing this gameweek |
| `chance_of_playing_next_round` | int | Probability (0-100) of playing next gameweek |
| `special` | bool | Whether player has special status |
| `removed` | bool | Whether player has been removed from the game |
| `can_select` | bool | Whether player can be selected |
| `can_transact` | bool | Whether player can be transferred |
| `has_temporary_code` | bool | Whether player has a temporary code |

### Pricing & Value

| Column | Type | Description |
|--------|------|-------------|
| `now_cost` | int | Current price in £0.1m units (e.g., 100 = £10.0m) |
| `cost_change_event` | int | Price change this gameweek (in £0.1m) |
| `cost_change_event_fall` | int | Price drops this gameweek |
| `cost_change_start` | int | Total price change since season start |
| `cost_change_start_fall` | int | Total price drops since season start |
| `now_cost_rank` | int | Rank by current cost (all players) |
| `now_cost_rank_type` | int | Rank by current cost (within position) |
| `value_form` | str | Points per £1m based on recent form |
| `value_season` | str | Points per £1m for the season |

### Points & Performance

| Column | Type | Description |
|--------|------|-------------|
| `total_points` | int | Total FPL points scored this season |
| `event_points` | int | Points scored in the current/latest gameweek |
| `points_per_game` | str | Average points per game played |
| `points_per_game_rank` | int | Rank by points per game (all players) |
| `points_per_game_rank_type` | int | Rank by points per game (within position) |
| `form` | str | Average points over last 30 days |
| `form_rank` | int | Rank by form (all players) |
| `form_rank_type` | int | Rank by form (within position) |
| `ep_this` | str | Expected points this gameweek |
| `ep_next` | str | Expected points next gameweek |

### Playing Time

| Column | Type | Description |
|--------|------|-------------|
| `minutes` | int | Total minutes played this season |
| `starts` | int | Number of starts this season |
| `starts_per_90` | str | Starts per 90 minutes |

### Goals & Assists

| Column | Type | Description |
|--------|------|-------------|
| `goals_scored` | int | Goals scored this season |
| `assists` | int | Assists this season |
| `own_goals` | int | Own goals this season |
| `penalties_missed` | int | Penalties missed this season |

### Defensive Stats

| Column | Type | Description |
|--------|------|-------------|
| `clean_sheets` | int | Clean sheets this season |
| `clean_sheets_per_90` | str | Clean sheets per 90 minutes |
| `goals_conceded` | int | Goals conceded while on pitch |
| `goals_conceded_per_90` | str | Goals conceded per 90 minutes |
| `saves` | int | Saves made (goalkeepers) |
| `saves_per_90` | str | Saves per 90 minutes |
| `penalties_saved` | int | Penalties saved (goalkeepers) |

### Additional Stats

| Column | Type | Description |
|--------|------|-------------|
| `tackles` | int | Tackles made this season |
| `recoveries` | int | Ball recoveries this season |
| `clearances_blocks_interceptions` | int | Defensive actions (clearances + blocks + interceptions) |
| `defensive_contribution` | str | Defensive contribution metric |
| `defensive_contribution_per_90` | str | Defensive contribution per 90 minutes |

### Cards

| Column | Type | Description |
|--------|------|-------------|
| `yellow_cards` | int | Yellow cards received this season |
| `red_cards` | int | Red cards received this season |

### Bonus Points System (BPS)

| Column | Type | Description |
|--------|------|-------------|
| `bonus` | int | Total bonus points this season |
| `bps` | int | Total Bonus Points System score |

### ICT Index

The ICT Index is FPL's proprietary metric measuring player performance.

| Column | Type | Description |
|--------|------|-------------|
| `ict_index` | str | Combined ICT score (Influence + Creativity + Threat) |
| `ict_index_rank` | int | ICT rank (all players) |
| `ict_index_rank_type` | int | ICT rank (within position) |
| `influence` | str | Influence score - measures impact on matches |
| `influence_rank` | int | Influence rank (all players) |
| `influence_rank_type` | int | Influence rank (within position) |
| `creativity` | str | Creativity score - measures chance creation |
| `creativity_rank` | int | Creativity rank (all players) |
| `creativity_rank_type` | int | Creativity rank (within position) |
| `threat` | str | Threat score - measures goal threat |
| `threat_rank` | int | Threat rank (all players) |
| `threat_rank_type` | int | Threat rank (within position) |

### Expected Stats (xG)

| Column | Type | Description |
|--------|------|-------------|
| `expected_goals` | str | Expected goals (xG) this season |
| `expected_goals_per_90` | str | xG per 90 minutes |
| `expected_assists` | str | Expected assists (xA) this season |
| `expected_assists_per_90` | str | xA per 90 minutes |
| `expected_goal_involvements` | str | xG + xA combined |
| `expected_goal_involvements_per_90` | str | xGI per 90 minutes |
| `expected_goals_conceded` | str | Expected goals conceded (xGC) |
| `expected_goals_conceded_per_90` | str | xGC per 90 minutes |

### Transfers & Selection

| Column | Type | Description |
|--------|------|-------------|
| `selected_by_percent` | str | Percentage of FPL managers who own this player |
| `selected_rank` | int | Rank by ownership (all players) |
| `selected_rank_type` | int | Rank by ownership (within position) |
| `transfers_in` | int | Total transfers in this season |
| `transfers_out` | int | Total transfers out this season |
| `transfers_in_event` | int | Transfers in this gameweek |
| `transfers_out_event` | int | Transfers out this gameweek |

### Dream Team

| Column | Type | Description |
|--------|------|-------------|
| `in_dreamteam` | bool | Whether player is in current Dream Team |
| `dreamteam_count` | int | Number of times in Dream Team this season |

### Set Pieces

| Column | Type | Description |
|--------|------|-------------|
| `penalties_order` | int | Penalty taking priority (null if not on penalties) |
| `penalties_text` | str | Description of penalty taking status |
| `direct_freekicks_order` | int | Direct free kick priority |
| `direct_freekicks_text` | str | Description of direct FK status |
| `corners_and_indirect_freekicks_order` | int | Corners/indirect FK priority |
| `corners_and_indirect_freekicks_text` | str | Description of corners status |

---

## cleaned_players.csv

A simplified version of players_raw.csv with key columns.

| Column | Type | Description |
|--------|------|-------------|
| `first_name` | str | Player's first name |
| `second_name` | str | Player's surname |
| `goals_scored` | int | Goals scored this season |
| `assists` | int | Assists this season |
| `total_points` | int | Total FPL points |
| `minutes` | int | Minutes played |
| `goals_conceded` | int | Goals conceded |
| `creativity` | str | Creativity ICT score |
| `influence` | str | Influence ICT score |
| `threat` | str | Threat ICT score |
| `bonus` | int | Bonus points |
| `bps` | int | BPS total |
| `ict_index` | str | Combined ICT index |
| `clean_sheets` | int | Clean sheets |
| `red_cards` | int | Red cards |
| `yellow_cards` | int | Yellow cards |
| `selected_by_percent` | str | Ownership percentage |
| `now_cost` | int | Current price (in £0.1m) |
| `element_type` | str | Position (GK/DEF/MID/FWD) |
| `value_per_m` | float | Points per £1m (total_points / (now_cost/10)) |

---

## Gameweek Files (gw*.csv)

Individual gameweek performance data for all players.

### Player Info

| Column | Type | Description |
|--------|------|-------------|
| `name` | str | Player's full name |
| `position` | str | Position (GK/DEF/MID/FWD) |
| `team` | str | Team name |
| `element` | int | Player FPL ID |

### Match Context

| Column | Type | Description |
|--------|------|-------------|
| `fixture` | int | Fixture ID |
| `round` | int | Gameweek number |
| `opponent_team` | int | Opponent team ID |
| `was_home` | bool | True if home game, False if away |
| `kickoff_time` | str | Match kickoff datetime (ISO format) |
| `team_h_score` | int | Home team final score |
| `team_a_score` | int | Away team final score |

### Performance

| Column | Type | Description |
|--------|------|-------------|
| `total_points` | int | FPL points scored in this GW |
| `minutes` | int | Minutes played |
| `starts` | int | 1 if started, 0 if substitute |
| `goals_scored` | int | Goals in this match |
| `assists` | int | Assists in this match |
| `clean_sheets` | int | 1 if clean sheet, 0 otherwise |
| `goals_conceded` | int | Goals conceded while on pitch |
| `own_goals` | int | Own goals scored |
| `penalties_saved` | int | Penalties saved |
| `penalties_missed` | int | Penalties missed |
| `saves` | int | Saves made |
| `yellow_cards` | int | Yellow cards received |
| `red_cards` | int | Red cards received |
| `bonus` | int | Bonus points (0-3) |
| `bps` | int | BPS score for this match |

### ICT & Expected Stats

| Column | Type | Description |
|--------|------|-------------|
| `ict_index` | str | ICT index for this match |
| `influence` | str | Influence score |
| `creativity` | str | Creativity score |
| `threat` | str | Threat score |
| `expected_goals` | str | xG for this match |
| `expected_assists` | str | xA for this match |
| `expected_goal_involvements` | str | xGI for this match |
| `expected_goals_conceded` | str | xGC for this match |

### Additional GW Stats

| Column | Type | Description |
|--------|------|-------------|
| `xP` | float | Expected points (predicted before match) |
| `value` | int | Player price at this gameweek (in £0.1m) |
| `selected` | int | Number of managers who owned this player |
| `transfers_in` | int | Transfers in this GW |
| `transfers_out` | int | Transfers out this GW |
| `transfers_balance` | int | Net transfers (in - out) |
| `modified` | bool | Whether data was modified/corrected |

### Defensive Stats (when available)

| Column | Type | Description |
|--------|------|-------------|
| `tackles` | int | Tackles made |
| `recoveries` | int | Ball recoveries |
| `clearances_blocks_interceptions` | int | Defensive actions |
| `defensive_contribution` | str | Defensive contribution metric |

### Manager Points (2024-25 Season onwards)

| Column | Type | Description |
|--------|------|-------------|
| `mng_clean_sheets` | int | Manager clean sheet points |
| `mng_draw` | int | Manager draw points |
| `mng_goals_scored` | int | Manager goals scored points |
| `mng_loss` | int | Manager loss points |
| `mng_underdog_draw` | int | Manager underdog draw bonus |
| `mng_underdog_win` | int | Manager underdog win bonus |
| `mng_win` | int | Manager win points |

---

## fixtures.csv

All fixtures for the season.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Fixture ID |
| `event` | int | Gameweek number (null if not yet scheduled) |
| `team_h` | int | Home team ID |
| `team_a` | int | Away team ID |
| `team_h_score` | int | Home team score (null if not played) |
| `team_a_score` | int | Away team score (null if not played) |
| `kickoff_time` | str | Scheduled kickoff (ISO format) |
| `finished` | bool | Whether match has finished |
| `started` | bool | Whether match has started |
| `finished_provisional` | bool | Provisionally finished |
| `minutes` | int | Minutes played |
| `team_h_difficulty` | int | Fixture difficulty for home team (1-5) |
| `team_a_difficulty` | int | Fixture difficulty for away team (1-5) |

---

## teams.csv

Team information.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Team ID (1-20) |
| `code` | int | Internal team code |
| `name` | str | Full team name |
| `short_name` | str | 3-letter abbreviation |
| `strength` | int | Overall team strength rating |
| `strength_overall_home` | int | Home strength |
| `strength_overall_away` | int | Away strength |
| `strength_attack_home` | int | Home attacking strength |
| `strength_attack_away` | int | Away attacking strength |
| `strength_defence_home` | int | Home defensive strength |
| `strength_defence_away` | int | Away defensive strength |

---

## Player History Files

Located in `players/<player_name>_<id>/`

### gw.csv

Gameweek-by-gameweek stats for the player (same columns as main GW files).

### history.csv

Historical season data for players who have previous FPL history.

| Column | Type | Description |
|--------|------|-------------|
| `season_name` | str | Season (e.g., "2023/24") |
| `element_code` | int | Player code |
| `start_cost` | int | Price at season start |
| `end_cost` | int | Price at season end |
| `total_points` | int | Total points that season |
| `minutes` | int | Total minutes |
| `goals_scored` | int | Goals |
| `assists` | int | Assists |
| `clean_sheets` | int | Clean sheets |
| `goals_conceded` | int | Goals conceded |
| `own_goals` | int | Own goals |
| `penalties_saved` | int | Penalties saved |
| `penalties_missed` | int | Penalties missed |
| `yellow_cards` | int | Yellow cards |
| `red_cards` | int | Red cards |
| `saves` | int | Saves |
| `bonus` | int | Bonus points |
| `bps` | int | BPS total |
| `influence` | str | Influence score |
| `creativity` | str | Creativity score |
| `threat` | str | Threat score |
| `ict_index` | str | ICT index |

---

## Understat Data

Located in `understat/` directory. Contains advanced expected goals data from [understat.com](https://understat.com).

### understat_player.csv

Overview of all EPL players with Understat data.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Understat player ID |
| `player_name` | str | Player name |
| `games` | int | Games played |
| `time` | int | Minutes played |
| `goals` | int | Goals scored |
| `xG` | float | Expected goals |
| `assists` | int | Assists |
| `xA` | float | Expected assists |
| `shots` | int | Total shots |
| `key_passes` | int | Key passes |
| `yellow_cards` | int | Yellow cards |
| `red_cards` | int | Red cards |
| `position` | str | Position(s) played |
| `team_title` | str | Team name |
| `npg` | int | Non-penalty goals |
| `npxG` | float | Non-penalty xG |
| `xGChain` | float | xG Chain (involvement in goal-scoring chains) |
| `xGBuildup` | float | xG Buildup (contribution to build-up play) |

### Player Match Files (<player_name>_<id>.csv)

Match-by-match Understat data for individual players.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Match ID |
| `season` | int | Season year |
| `position` | str | Position played |
| `h_team` | str | Home team |
| `a_team` | str | Away team |
| `h_goals` | int | Home goals |
| `a_goals` | int | Away goals |
| `date` | str | Match date |
| `time` | int | Minutes played |
| `goals` | int | Goals scored |
| `assists` | int | Assists |
| `shots` | int | Shots |
| `key_passes` | int | Key passes |
| `xG` | float | Expected goals |
| `xA` | float | Expected assists |
| `npg` | int | Non-penalty goals |
| `npxG` | float | Non-penalty xG |
| `xGChain` | float | xG Chain |
| `xGBuildup` | float | xG Buildup |

### id_dict.csv

Mapping between Understat IDs and FPL IDs.

| Column | Type | Description |
|--------|------|-------------|
| `Understat_ID` | int | Understat player ID (-1 if not found) |
| `FPL_ID` | int | FPL player ID (-1 if not found) |
| `Understat_Name` | str | Name in Understat |
| `FPL_Name` | str | Name in FPL |

---

## Notes

### Position Codes
- 1 = GK (Goalkeeper)
- 2 = DEF (Defender)
- 3 = MID (Midfielder)
- 4 = FWD (Forward)
- 5 = AM (Attacking Midfielder - used in some older seasons)

### Pricing
All costs are stored in £0.1m units. Divide by 10 to get the actual price in millions.
- Example: `now_cost = 100` means the player costs £10.0m

### Expected Stats (xG/xA)
- **xG (Expected Goals)**: Statistical measure of the quality of chances created
- **xA (Expected Assists)**: Statistical measure of passes that led to shots
- **xGI (Expected Goal Involvements)**: xG + xA combined
- **xGC (Expected Goals Conceded)**: Expected goals conceded based on shots faced

### ICT Index
FPL's proprietary performance metric:
- **Influence**: Impact on single matches via goals, assists, and other contributions
- **Creativity**: Chance creation through passing and crossing
- **Threat**: Scoring threat based on shots and positions

### BPS (Bonus Points System)
A scoring system used to determine bonus points (1-3) awarded to the top performers in each match.

---

## Contributing

If you notice any missing or incorrect variable descriptions, please open an issue or submit a PR!

