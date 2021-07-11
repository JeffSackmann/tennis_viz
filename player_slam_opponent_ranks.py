# -*- coding: utf-8 -*-
import altair as alt
import pandas as pd

## path to repo with relevant data
## ( https://github.com/JeffSackmann/tennis_atp )
data_prefix = '../tennis_atp/'

## note that the tennis_atp repo does not contain matches from the current week's
## tournaments and may not be completely up to date otherwise, so some matches 
## can be manually added below.

player = 'Novak Djokovic'

keep_columns = ['tourney_date', 'tourney_name', 'opp_rank', 'is_final', 'result', 'opponent', 'round']
player_slam_matches = []
for y in range(2005,2022):
    ## load matches and reduce to the target player, in first four rounds at slams
    matches = pd.read_csv(data_prefix + 'atp_matches_' + str(y) + '.csv')
    matches.astype({'round': 'object'}).dtypes
    pmatches = matches.loc[(matches['winner_name'] == player) | (matches['loser_name'] == player)]
    pmatches = pmatches.loc[(pmatches['tourney_level'] == 'G') & (pmatches['score'] != 'W/O')]
    
    ## add columns for opponent rank and winner/loser flag (from perspective of the target player)
    pmatches['opp_rank'] = pmatches.apply(lambda row: row.loser_rank 
                                          if row.winner_name == player else row.winner_rank, axis=1)
    pmatches['opponent'] = pmatches.apply(lambda row: row.loser_name 
                                          if row.winner_name == player else row.winner_name, axis=1)
    pmatches['result'] = pmatches.apply(lambda row: 'W' if row.winner_name == player else 'L', axis=1)
    pmatches['is_final'] = pmatches.apply(lambda row: 'Final' if row['round'] == 'F' else 'Other', axis=1)
    
    ## this method only works if replacing a single null opp_rank
    ## At 2007 Wimb, Kiefer was unranked, but had recently been 404
    pmatches['opp_rank'] = pmatches['opp_rank'].fillna(404.0)
    
    y_summary = pd.DataFrame(pmatches, columns=keep_columns).values.tolist()  
    player_slam_matches += y_summary                                                          
    
## add 2021 wimbledon, not yet in the tennis_atp data
manual_add = [[20210628, 'Wimbledon', 253, 'Other', 'W', 'Jack Draper', 'R128'],
              [20210628, 'Wimbledon', 102, 'Other', 'W', 'Kevin Anderson', 'R64'],
              [20210628, 'Wimbledon', 114, 'Other', 'W', 'Denis Kudla', 'R32'],
              [20210628, 'Wimbledon', 20, 'Other', 'W' ,'Cristian Garin', 'R16'],
              [20210628, 'Wimbledon', 48, 'Other', 'W', 'Marton Fucsovics', 'QF'],
              [20210628, 'Wimbledon', 12, 'Other', 'W', 'Denis Shapovalov', 'SF'],
              [20210628, 'Wimbledon', 9, 'Final', '?', 'Matteo Berrettini', 'F']
              ]
player_slam_matches += manual_add

## sort slams ascending by date
player_slam_matches = sorted(player_slam_matches, key=lambda x: x[0])

slam_abvs = {'Wimbledon': 'Wimb',
             'US Open': 'USO',
             'Us Open': 'USO',
             'Australian Open': 'AO',
             'Roland Garros': 'RG'
             }

## abbreviated names of tournaments where the plot looks better
## with labels above the point instead of below it
manual_uppers = ['2007 Wimb', '2012 AO', '2013 USO', '2015 USO',
                 '2016 RG', '2017 Wimb', '2006 AO', '2018 RG',
                 '2005 Wimb', '2009 Wimb']

name_abvs = {'Roger Federer': 'Fed',
            'Rafael Nadal': 'Rafa',
            'Andy Murray': 'Muzz',
            'Stan Wawrinka': 'Stan',
            'Pablo Carreno Busta': 'PCB',
            'Juan Martin del Potro': 'Delpo',
            'Philipp Kohlschreiber': 'Kohli',
            'Kei Nishikori': 'Kei'}

def add_label(row):
    tdate, tname, opp_rank, _, result, opp_name, rd = row
    full_name = str(tdate)[:4] + ' ' + slam_abvs[tname]
    
    ## get opponent name (or abbreviation) label
    ## (if a final, a loss, or opponent is #1)
    need_label, label = 0, ''
    if result != 'W' or rd == 'F':
        need_label = 1
    elif opp_rank == 1:
        need_label = 1
        
    if need_label:
        ## use label specified in name_abvs or, if not available, use last name 
        label = name_abvs[opp_name] if opp_name in name_abvs else opp_name.split(' ')[-1]
        
    if full_name in manual_uppers:
        output = row[2:] + ['', label]
    else:
        output = row[2:] + [label, '']
    output.append(full_name)
    return output

labeled_matches = [add_label(k) for k in player_slam_matches]    

## replace opp_rank = 1 with 1.25, to move matches vs #1 players up off of the bottom horizontal axis
matches = [k if k[0] != 1 else [1.25] + k[1:] for k in labeled_matches]
    
df = pd.DataFrame(matches, columns=['Opponent Rank', 'Round', 'Result', 'Opponent', 
                                    'round_short', 'Label Lower', 'Label Upper', 'FullName'])

df['Tooltip'] = df.apply(lambda row: row['FullName'] + ' ' + row['round_short'] + ' vs #' + str(int(row['Opponent Rank'])) + ' ' + row['Opponent'], axis=1)

## store list in *date* order for the chart to use:
x_sort = df['FullName'].tolist()

## separate title-winning finals from other matches in order to differently size the points
title_finals = df.loc[(df['Result'] != 'L') & (df['Round'] == 'Final')]
other_matches = df.loc[(df['Result'] == 'L') | (df['Round'] != 'Final')]
## results only to be used for calculating won-loss record (exclude pending match)
results_only = df.loc[(df['Result'] != '?')]

chart_title = player + ' Matches at Grand Slams'

brush = alt.selection(type='interval')

## line chart with all matches (except title-winning finals)
points = alt.Chart(other_matches).mark_point(filled=True, size=60).encode(
    alt.X('FullName',
          sort=x_sort,
          axis=alt.Axis(title='Tournament')),
    alt.Y('Opponent Rank',
          axis=alt.Axis(title='Opponent Ranks',
                        values=[5, 10, 20, 50, 100, 250]
                        ),
          scale=alt.Scale(domain=(1, 600),
                          type='log',
                          base=3)),
    color=alt.Color('Result',
                    scale=alt.Scale(
                    domain=['W', 'L', '?'],
                    range=['purple', 'red', 'orange'])),
    shape=alt.Shape('Round',
                    scale=alt.Scale(
                    domain=['Final', 'Other'],
                    range=['square', 'circle'])),
    tooltip='Tooltip:N'
)

## add bigger points for title-winning finals    
titles = alt.Chart(title_finals).mark_point(filled=True, size=120).encode(
    alt.X('FullName:N',
          sort=x_sort,
          ),
    alt.Y('Opponent Rank:Q'),
    color=alt.Color('Result',
                    scale=alt.Scale(
                    domain=['W', 'L', '?'],
                    range=['purple', 'red', 'orange'])),
    shape=alt.Shape('Round',
                    scale=alt.Scale(
                    domain=['Final', 'Other'],
                    range=['square', 'circle'])),
    tooltip='Tooltip:N',
)

## vertical lines for each tournament -- opacity level is *per match*,
## so opacity depends on how many matches played at that event. Could
## change that by using a list of unique tournament names only.
rules = alt.Chart(df).mark_rule(opacity=0.01).encode(
    alt.X('FullName:N',
          sort=x_sort,
          )
)
    
## four separate caption layers:
## for lower/upper and title-winning finals/other matches
text_lower = points.mark_text(
    align='left',
    baseline='line-top',
    dx=5,
    dy=1
).encode(
    text='Label Lower'
)
    
text_upper = points.mark_text(
    align='left',
    baseline='line-bottom',
    dx=5,
    dy=-1
).encode(
    text='Label Upper'
)
    
text_lower_titles = titles.mark_text(
    align='left',
    baseline='line-top',
    dx=6,
    dy=3
).encode(
    text='Label Lower'
)
    
text_upper_titles = titles.mark_text(
    align='left',
    baseline='line-bottom',
    dx=5,
    dy=-3
).encode(
    text='Label Upper'
)
    
layered = alt.layer(points, titles, text_lower, text_upper, text_lower_titles, text_upper_titles, rules).add_selection(
    brush
).properties(
    width=1200,
    height=400,
    title=chart_title
)
    
## bar chart with wins and losses from highlighted section
bars = alt.Chart(results_only).mark_bar().encode(
    alt.X('count(Result):Q',
          axis=alt.Axis(title='Won-Loss Record (highlight section above to update)',
                        labels=False,
                        ticks=False)
          ),
    alt.Y('Result:N',
          sort=['W', 'L']
          ),
    color='Result:N'
)

## text overlay for the bar chart  
bar_text = alt.Chart(results_only).mark_text(dx=-10, dy=3, color='white').encode(
    x=alt.X('count(Result):Q', stack='zero'),
    y=alt.Y('Result:N',
            sort=['W', 'L'],
            ),
    text=alt.Text('count(Result):Q', format='.0f')
)

bar_layer = alt.layer(bars, bar_text).transform_filter(
    brush
).properties(
    width=1200
)
    
combined = alt.vconcat(layered, bar_layer).configure_axisX(
    labelAngle=300
).configure_legend(
    titleFontSize=14,
    labelFontSize=12
).save('output/djokovic_slam_opponent_ranks.html')