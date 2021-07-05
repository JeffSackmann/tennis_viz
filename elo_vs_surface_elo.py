# -*- coding: utf-8 -*-
import altair as alt
import pandas as pd

## Elo ratings available here: http://tennisabstract.com/reports/wta_elo_ratings.html
## csv is reduced to one column each for overall Elo and "GrassRaw" Elo
## note: grass Elo is based only on grass-court results
## (code to generate ratings is not public)

df = pd.read_csv('data/20210705_wta_gElo.csv')
df.astype({'Elo': 'float', 
           'GrassRaw': 'float',
           'still_in': 'int'
           }).dtypes

## label only players remaining in the tournament
## (still_in is boolean variable manually added to the data input)
df['label'] = df.apply(lambda row: row.Player if row.still_in == 1 else '', axis=1)
    
## probably should automate setting the domains of each axis; 
## I added a bit extra to the high-end of the X-axis to make room for a label
points = alt.Chart(df).mark_circle(size=60).encode(
    alt.X('Elo:Q',
          scale=alt.Scale(domain=(1300,2350)),
          axis=alt.Axis(title='Overall Elo')
          ),
    alt.Y('GrassRaw:Q',
          scale=alt.Scale(domain=(1200,1900)),
          axis=alt.Axis(title='Grass-Only Elo')
          ),
    color=alt.Color('still_in', legend=None),
)

text = points.mark_text(
    align='left',
    baseline='middle',
    dx=7
).encode(
    text='label'
)

combined = points + text
combined.save('output/wta_elo_vs_gElo.html')




