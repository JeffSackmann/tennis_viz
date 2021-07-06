# -*- coding: utf-8 -*-
import altair as alt
import pandas as pd

## path to repo with relevant data
## ( https://github.com/JeffSackmann/tennis_slam_pointbypoint )
data_prefix = '../tennis_slam_pointbypoint/'

year, tourney = '2021', 'wimbledon'

## load tournament data:
matches = pd.read_csv(data_prefix + year + '-' + tourney + '-matches.csv')
points = pd.read_csv(data_prefix + year + '-' + tourney + '-points.csv')
mpoints = pd.merge(points, matches).fillna(0)

mpoints.astype({'PointWinner': 'int',
                'P1Winner': 'int',
                'P2Winner': 'int',
                'P1UnfErr': 'int',
                'P2UnfErr': 'int'
                }).dtypes

## skip points without a winner (placeholders when matches are starting, etc)
mpoints = mpoints.loc[mpoints['PointWinner'] != 0]

## get list of (women's) players who reached R3
womens_third = matches.loc[(matches['match_id'].str[-4] == '2') & (matches['match_id'].str[-3] == '3')]
r3_players = womens_third['player1'].tolist() + womens_third['player2'].tolist()

## get winner rate and unforced error rate for each player
player_rates = []
for player in r3_players:
    ppoints = mpoints.loc[(mpoints['player2'] == player) | (mpoints['player1'] == player)]
    winners_as_1 = ppoints.loc[(ppoints['P1Winner'] == 1) & (ppoints['player1'] == player)]
    winners_as_2 = ppoints.loc[(ppoints['P2Winner'] == 1) & (ppoints['player2'] == player)]
    errors_as_1 = ppoints.loc[(ppoints['P1UnfErr'] == 1) & (ppoints['player1'] == player)]
    errors_as_2 = ppoints.loc[(ppoints['P2UnfErr'] == 1) & (ppoints['player2'] == player)]
    n_points = len(ppoints)
    n_winners = len(winners_as_1) + len(winners_as_2)
    n_errors = len(errors_as_1) + len(errors_as_2)
    winner_rate = n_winners / float(n_points)
    error_rate = n_errors / float(n_points)
    ## is player still in the tournament? (did she win her last point?)
    last_point = ppoints.tail(1)
    still_in = 0.5
    if last_point['player1'].item() == player and last_point['PointWinner'].item() == 1:
        still_in = 1
    elif last_point['player2'].item() == player and last_point['PointWinner'].item() == 2:
        still_in = 1
    player_row = [player, winner_rate, error_rate, still_in]
    player_rates.append(player_row)


rates_header = ['Player', 'Winner Perc', 'Error Perc', 'still_in']
df = pd.DataFrame(player_rates, columns=rates_header)

## label only players remaining in the tournament (with last name only)
## (still_in is boolean variable manually added to the data input)
df['label'] = df.apply(lambda row: row.Player.split(' ')[-1] if row.still_in == 1 else '', axis=1)
    
points = alt.Chart(df).mark_circle(size=60).encode(
    alt.X('Error Perc:Q',
          scale=alt.Scale(domain=(0.1,0.24)),
          axis=alt.Axis(format='%',
                        title='Unforced Error Rate (ufe per point)')
          ),
    alt.Y('Winner Perc:Q',
          scale=alt.Scale(domain=(0.05, 0.24)),
          axis=alt.Axis(format='%',
                        title='Winner Rate (winners per point)')
          ),
    ## 'N' treats still_in as nominal, not a quantitative scale, so just picks
    ## two different colors
    color=alt.Color('still_in:N', legend=None),
)

text = points.mark_text(
    align='left',
    baseline='middle',
    dx=7
).encode(
    text='label'
)

## strokeDash gives dotted line
reg_line = points.transform_regression('Error Perc', 'Winner Perc').mark_line(strokeDash=[1,1])

## the 'category' list specifies colors for the two options of 'still_in'
combined = (points + text + reg_line).configure_range(
    category=['#00008B', '#B0E0E6'] ##{'scheme': 'dark2'}
)
combined.save('output/wimbledon_wta_winners_vs_ufe.html')




