[![GitSpo Mentions](https://gitspo.com/badges/mentions/vaastav/Fantasy-Premier-League?style=flat-square)](https://gitspo.com/mentions/vaastav/Fantasy-Premier-League)
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=RQ2V64LXSKPV4)

Fantasy-Premier-League
======================

A FPL library that gets all the basic stats for each player, gw-specific data for each player and season history of each player

### How to CIte this dataset?

BibTeX:

```
@misc{anand2016fantasypremierleague,
  title = {{FPL Historical Dataset}},
  author = {Anand, Vaastav},
  year = {2022},
  howpublished = {Retrieved August 2022 from \url{https://github.com/vaastav/Fantasy-Premier-League/}}
}
```


### Acknowledgement

+ rin-hairie for adding master team lists and merge scripts
+ ergest for adding merged_gw.csv files for 2016-17 and 2017-18 seasons
+ BDooley11 for providing top managers script
+ speeder1987 for providing 2018/19 fixtures.csv file
+ ravgeetdhillon for github actions automation for data update
+ kz4killua for fixing GW37 data for the 21-22 season
+ SaintJuniper for id-dictionary update for the 21-22 season

## FAQ

### Data Structure

The data folder contains the data from past seasons as well as the current season. It is structured as follows:

+ season/cleaned_players.csv : The overview stats for the season
+ season/gws/gw_number.csv : GW-specific stats for the particular season
+ season/gws/merged_gws.csv : GW-by-GW stats for each player in a single file
+ season/players/player_name/gws.csv : GW-by-GW stats for that specific player
+ season/players/player_name/history.csv : Prior seasons history stats for that specific player.

### Player Position Data

In players_raw.csv, element_type is the field that corresponds to the position.
1 = GK
2 = DEF
3 = MID
4 = FWD

### Errata

+ GW35 expected points data is wrong (all values are 0).

### Contributing

+ If you feel like there is some data that is missing which you would like to see, then please feel free to create a PR or create an issue highlighting what is missing and what you would like to be added
+ If you have access to old data (pre-2016) then please feel free to create Pull Requests adding the data to the repo or create an issue with links to old data and I will add them myself.

### Using

If you use data from here for your website or blog posts, then I would humbly request that you please add a link back to this repo as the data source (and I would in turn add a link to your post/site as a notable usage of this repo).

## Downloading Your Team Data

You can download the data for your team by executing the following steps:

```
python teams_scraper.py <team_id>
#Eg: python teams_scraper.py 4582
```

This will create a new folder called "team_<team_id>_data18-19" with individual files of all the important data

# Notable Usages of this Repository

+ [Analysing Fantasy Premier League data in R Course by Arif P. Sulistiono](https://github.com/arifpras/BelutListrik)

+ [Point Predictor via Random Forests by Francesco Barbara](https://github.com/francescobarbara/FPL-point-predictor-via-random-forests)

+ [Money (Foot)Ball – how will our virtual football team selected entirely by Machine Learning compete in the big leagues?](https://www.dtsquared.co.uk/money-football-how-will-our-virtual-football-team-selected-entirely-by-machine-learning-compete-in-the-big-leagues/)

+ [An introduction to SQL using FPL data by Liam Connors](https://towardsdatascience.com/an-introduction-to-sql-using-fpl-data-8314ec982308)

+ [Hindsight Optimization for FPL by Sertalp B. Cay](https://alpscode.com/blog/hindsight-optimization/)

+ [Data Science to get top 1% on return to FPL by James Asher](https://medium.com/the-sports-scientist/how-i-used-data-science-to-get-into-the-top-1-on-the-return-to-fantasy-premier-league-98829d4f65e5)

+ [FPLDASH: A customizable Fantasy Premier League Dashboard by Jin Hyun Cheong](http://www.fpldash.com)

+ [How to win at Fantasy Football with Splunk and Machine Learning by Rupert Truman](https://www.splunk.com/en_us/blog/machine-learning/how-to-win-at-fantasy-football-with-splunk-and-machine-learning-part-1.html)

+ [2019-20 Winner Joshua Bull's Oxford Maths Public Lecture](https://www.youtube.com/watch?v=LzEuweGrHvc)

+ [2019-20 Lottery Analysis by @theFPLKiwi](https://twitter.com/theFPLkiwi/status/1297619700206239746?s=20)

+ [Fantasy Nutmeg Website by code247](https://www.fantasynutmeg.com/history)

+ [Fantasy Premier League 19/20, a review by Hersh Dhillon](https://medium.com/@2017csb1079/fantasy-premier-league-19-20-a-review-part-1-basics-167e610e229)

+ [Visualisasi Data: Fantasy Premier League 19/20 by Erwindra Rusli](https://medium.com/@erwindrarusli/visualisasi-data-fantasy-premier-league-19-20-a80aaf097a21)

+ [Machine Learning Model by pratz](https://keytodatascience.com/fpl-machine-learning/)

+ [xA vs xG for Attacking Midfielders/Forwards by u/JLane1996](https://www.reddit.com/r/FantasyPL/comments/erfdy1/a_plot_of_xg_vs_xa_for_for_attacking_midsforwards/)

+ [Expected Goals vs Actual Goals for Manchester United by u/JLane1996](https://www.reddit.com/r/reddevils/comments/ecbn9j/corrected_plot_of_goals_vs_expected_goals_this/fba8vs3/)

+ [Tableau Viz by u/richkelana](https://www.reddit.com/r/tableau/comments/e2j0uq/my_first_tableu_viz_fpl/)

+ [Top Players against GW13 rival by u/LiuSiuMing](https://www.reddit.com/r/FantasyPL/comments/dz04hf/top_players_against_gw13_rival/)

+ [Captaincy Choice GW4 2019-20 post by Matthew Barnfield](https://mbarnfield.github.io/fpl.html)

+ [Building a dataset for Fantasy Premier League analysis by djfinnoy](http://www.didjfin.no/blog/fpl/fantasy-premier-league-data/)

+ [Value in FPL 2019-20 Report by Who Got The Assist?](https://whogottheassist.com/value-in-fpl-2019-20-report/)

+ [Talisman Theory 2018-19 Report by Who Got The Assist?](https://whogottheassist.com/talisman-theory-part-one-2018-19-report/)

+ [Historical Analyses in fplscrapR by Rasmus Chrisentsen](https://twitter.com/fplscrapR)

+ [Linearly Optimising Fantasy Premier League Teams by Joseph O'Connor](https://medium.com/@joseph.m.oconnor.88/linearly-optimising-fantasy-premier-league-teams-3b76e9694877)

+ [How to Win at Fantasy Premier league using Deep learning by Paul Solomon](https://medium.com/@sol.paul/how-to-win-at-fantasy-premier-league-using-data-part-1-forecasting-with-deep-learning-bf121f38643a)

+ [graphql API by u/jeppews](https://api.better-fpl.com/graphql)

+ [FPL modeling and prediction by @alsgregory](https://github.com/alsgregory/Fantasy-Football)

+ [FPL.co.id Talismans by @FPL_COID](http://fpl.co.id/tools/talismans/)

+ [Leicester City Brendan Rodgers Impact Analysis on twitter by @neilswmurrayFPL](https://twitter.com/neilswmurrayFPL/status/1147407501736009728)

+ [Stat Analysis on twitter by @StatOnScout](https://twitter.com/StatOnScout)

+ [Arsenal-Chelsea LinkedIn article by Velko Kamenov](https://www.linkedin.com/pulse/whoever-wins-2019-uefa-europe-league-final-still-ends-velko-kamenov/)

+ [Form vs Fixture Medium article by JinHyunCheong](https://towardsdatascience.com/mythbusting-fantasy-premier-league-form-over-fixtures-eecf9022e834)

+ [Visualization by u/dkattir](https://www.reddit.com/r/dataisbeautiful/comments/9zlx14/points_per_game_vs_predictability_after_12_weeks/)

+ [Visualization by u/Dray11](https://www.reddit.com/r/FantasyPL/comments/9bjwra/created_a_very_crude_and_basic_comparison_chart/)

+ [Visualization website by @antoniaelek](http://fantasy.elek.hr/)

+ [FPL Captain Classifier by Raghunandh GS](https://medium.com/datacomics/building-an-fpl-captain-classifier-cf4ee343ebcc)

+ [My Personal Blog](http://vaastavanand.com/blog/)

+ [FPL.cool](https://www.fpl.cool)
