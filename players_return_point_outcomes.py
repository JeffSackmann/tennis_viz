# -*- coding: utf-8 -*-
import altair as alt
import pandas as pd

## path to repo with relevant data
## ( https://github.com/JeffSackmann/tennis_slam_pointbypoint )
data_prefix = '../tennis_slam_pointbypoint/'

year = '2021'
tourney = 'wimbledon'
players = ['Ashleigh Barty', 'Karolina Pliskova', 'Aryna Sabalenka', 'Angelique Kerber']

matches = pd.read_csv(data_prefix + year + '-' + tourney + '-matches.csv')
points = pd.read_csv(data_prefix + year + '-' + tourney + '-points.csv')

## add match metadata to points rows
mpoints = pd.merge(points, matches).fillna(0)

player_outcomes = []
for p in players:    
    ## points with target player returning
    returning1 = mpoints.loc[(mpoints['PointServer'] == 2) & (mpoints['player1'] == p)]
    returning2 = mpoints.loc[(mpoints['PointServer'] == 1) & (mpoints['player2'] == p)]
    rpoints = pd.concat([returning1, returning2])
    
    df = rpoints.loc[(rpoints['P1DoubleFault'] == 1) | (rpoints['P2DoubleFault'] == 1)]
    ret_winner = rpoints.loc[(rpoints['PointServer'] != rpoints['PointWinner']) & (rpoints['RallyCount'] <= 3)]
    ret_other = rpoints.loc[(rpoints['PointServer'] != rpoints['PointWinner']) & (rpoints['RallyCount'] > 3)]
    
    aces = rpoints.loc[(rpoints['PointServer'] == rpoints['PointWinner']) & (rpoints['RallyCount'] <= 2)]
    plus_one = rpoints.loc[(rpoints['PointServer'] == rpoints['PointWinner']) & (rpoints['RallyCount'] <= 4)]
    sv_other = rpoints.loc[(rpoints['PointServer'] == rpoints['PointWinner']) & (rpoints['RallyCount'] > 4)]
    
    total = float(len(rpoints))
    player_outcomes += [[p, 'Double Faults', len(df) / total, 1],
                        [p, 'Return Winners', (len(ret_winner) - len(df)) / total, 2],
                        [p, 'Return Longer', len(ret_other) / total, 3],
                        [p, 'Serve Longer', len(sv_other) / total, 4],
                        [p, 'Serve + 1', (len(plus_one) - len(aces)) / total, 5],
                        [p, 'Serve Winners', len(aces) / total, 6],
                         ]

header = ['Player', 'Outcome', 'Percentage', 'Sort']
df = pd.DataFrame(player_outcomes, columns=header)
##df.astype({'KM/H': 'float', 
##            }).dtypes

    
chart = alt.Chart(df).mark_bar().encode(
    alt.X('sum(Percentage)',
          scale=alt.Scale(domain=(0, 1)),
          axis=alt.Axis(format='%', title='Percentage of return points'),
          ),
    order=alt.Order(
        'Sort',
        sort='ascending'
        ),
    y='Player',
    color=alt.Color('Outcome', sort=['Double Faults', 'Return Winners', 'Return Longer', 'Serve Longer', 'Serve + 1', 'Serve Winners'])
)

out_path = 'output/' + tourney + '_sfists_return_outcomes.html'
chart.save(out_path)




