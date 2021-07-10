# -*- coding: utf-8 -*-
import altair as alt
import pandas as pd

## path to repo with relevant data
## ( https://github.com/JeffSackmann/tennis_slam_pointbypoint )
data_prefix = '../tennis_slam_pointbypoint/'

year = '2021'
tourney = 'wimbledon'
players = ['Ashleigh Barty', 'Karolina Pliskova', 'Average']

matches = pd.read_csv(data_prefix + year + '-' + tourney + '-matches.csv')
points = pd.read_csv(data_prefix + year + '-' + tourney + '-points.csv')

## add match metadata to points rows
mpoints = pd.merge(points, matches).fillna(0)

## exclude points without a server:
mpoints = mpoints.loc[mpoints['PointServer'] != 0]
    
## exclude double faults:
serve_in_play = mpoints.loc[(mpoints['P1DoubleFault'] != 1) & (mpoints['P2DoubleFault'] != 1)]

## limit to women's points:
wpoints = serve_in_play.loc[serve_in_play['match_id'].str[-4] == '2']

output = [] ## rows of [Player [or average], Serve [All/1st/2nd], Return in play%]
for p in players:   
    ## points with target player returning (or all points if calculating averages)
    if p == 'Average':
        rpoints = wpoints
    else:
        returning1 = wpoints.loc[(wpoints['PointServer'] == 2) & (wpoints['player1'] == p)]
        returning2 = wpoints.loc[(wpoints['PointServer'] == 1) & (wpoints['player2'] == p)]
        rpoints = pd.concat([returning1, returning2])
    
    points_1st = rpoints.loc[rpoints['ServeNumber'] == 1]
    points_2nd = rpoints.loc[rpoints['ServeNumber'] == 2]
    
    ret_in_play = rpoints.loc[(rpoints['PointServer'] != rpoints['PointWinner']) | (rpoints['RallyCount'] >= 2)]
    in_play_1st = ret_in_play.loc[ret_in_play['ServeNumber'] == 1]
    in_play_2nd = ret_in_play.loc[ret_in_play['ServeNumber'] == 2]
    
    output += [[p, 'All Serves', len(ret_in_play) / float(len(rpoints))],
               [p, '1st Serves', len(in_play_1st) / float(len(points_1st))],
               [p, '2nd Serves', len(in_play_2nd) / float(len(points_2nd))]
               ]

header = ['Player', 'Serve', 'Returns in play']
df = pd.DataFrame(output, columns=header)

chart = alt.Chart(df).mark_bar().encode(
    alt.X('Player:N',
          sort=players,
          ),
    alt.Y('Returns in play:Q',
          axis=alt.Axis(format='%'),
          ),
    alt.Column('Serve:N',
               sort=['All Serves', '1st Serves', '2nd Serves'],
               header=alt.Header(title='')
               ),
    alt.Color('Player:N', 
              sort=players
              ),
    ) 


out_path = 'output/' + tourney + '_finalists_returns_in_play.html'
chart.save(out_path)




