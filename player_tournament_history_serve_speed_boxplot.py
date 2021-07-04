# -*- coding: utf-8 -*-
import altair as alt
import pandas as pd

## path to repo with relevant data:
data_prefix = '../tennis_slam_pointbypoint/'

player = 'Roger Federer'
tourney = 'wimbledon'

year_speeds = []
for year in ['2014', '2015', '2016', '2017', '2018', '2019', '2021']:
    matches = pd.read_csv(data_prefix + year + '-' + tourney + '-matches.csv')
    matches['year'] = matches['match_id'].str[:4]
    points = pd.read_csv(data_prefix + year + '-' + tourney + '-points.csv')
    
    ## add match metadata to points rows
    mpoints = pd.merge(points, matches).fillna(0)
    
    mpoints.astype({'PointServer': 'int',
                    'ServeNumber': 'int',
                    'Speed_KMH': 'int'
               }).dtypes
    
    ## skip  bad data with serve speed of zero
    mpoints = mpoints.loc[mpoints['Speed_KMH'] != 0]
    
    ## points with target player serving
    serving1 = mpoints.loc[(mpoints['PointServer'] == 1) & (mpoints['player1'] == player)]
    serving2 = mpoints.loc[(mpoints['PointServer'] == 2) & (mpoints['player2'] == player)]
    svpoints = pd.concat([serving1, serving2])
    
    ## first serve points from above
    fsv_points = svpoints.loc[svpoints['ServeNumber'] == 1]
    
    ## Rounds 1, 2, and 3 from above (round number is 3rd-to-last char in match_id)
    first_three_rounds = fsv_points.loc[fsv_points['match_id'].str[-3].isin(['1', '2', '3'])]
    
    ## reduce data to year and serve-speed only
    year_speeds += first_three_rounds[['year', 'Speed_KMH']].values.tolist()


df = pd.DataFrame(year_speeds, columns=['Year', 'KM/H'])
df.astype({'KM/H': 'float', 
            }).dtypes

serve_plot = alt.Chart(df).mark_boxplot().encode(
    alt.X('Year:N',
          ),
    alt.Y('KM/H:Q',
          scale=alt.Scale(domain=(120, 220))
          )
).properties(
    width=400,
    height=350
)

out_path = 'output/' + tourney + '_' + player.replace(' ', '_') + '_first_week_first_serves.html'
serve_plot.save(out_path)




