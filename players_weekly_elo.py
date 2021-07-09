# -*- coding: utf-8 -*-
import altair as alt
import pandas as pd

## current Elo ratings available here: http://tennisabstract.com/reports/atp_elo_ratings.html
## (historical ratings and code to generate ratings are not public)

## csv contains weekly elo ratings back to the beginning of 2018 for three players
df = pd.read_csv('data/wimb_sfists_weekly_elos.csv')
df.astype({'Elo': 'float', 
           'Date': 'datetime64',
           }).dtypes

## get list of the first ranking date in every month, for x-axis labels
dates_only = df.filter(['Date'], axis=1)
dates_only['year_month'] = dates_only.apply(lambda row: str(row['Date'])[:7], axis=1)
first_dates = dates_only.groupby('year_month').min()
first_date_list = first_dates['Date'].tolist()

## line chart with all tournaments
line = alt.Chart(df).mark_line().encode(
    alt.X('Date',
          axis=alt.Axis(title='Date',
                        values=first_date_list)),
    alt.Y('Elo',
          axis=alt.Axis(title='Overall Elo Rating'),
          scale=alt.Scale(domain=(1500,2050))),
    color='Player',
    strokeDash='Player'
).properties(
    width=800,
    height=300
)

line.save('output/wimb_sfists_weekly_elos.html')