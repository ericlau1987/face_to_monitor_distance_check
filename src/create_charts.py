# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import numpy as np

def data_processing(input: pd.DataFrame) -> pd.DataFrame:

    input['date'] = input['date_time'].dt.date.astype('datetime64')
    input['distances'] = round(df['distances'],2)
    return input

app = dash.Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

sqlEngine = create_engine('postgresql+psycopg2://postgres:postgres@postgres_distance_check/distance_check')
dbConnection = sqlEngine.connect()

df = pd.read_sql_query(
    """
    select *
    from distance
    where date(date_time) >= '2021-12-25'
    """
,dbConnection)

df = data_processing(df)

latest_date = max(df['date'])
df_latest_date = df[df['date'] == latest_date]
x = df_latest_date['date_time'].to_list()
y = df_latest_date['distances'].to_list()
y_distance_limit = df_latest_date['distance_limit'].to_list()

# Indicator for latest date
date_range = list(df['date'].unique())
date_range = sorted(date_range)
prior_date = date_range[-2] 
avg_distance_latest_date = np.mean(df_latest_date['distances'])
avg_distance_prior_date = np.mean(df[df['date'] == prior_date]['distances'])

fig_indicator = go.Figure()
fig_indicator.add_trace(go.Indicator(
    value = np.mean(avg_distance_latest_date),
    delta = {'reference': 50},
    gauge = {
        'axis': {'visible': False}},
    title = {'text': "Latest date: Average Distances vs Threshold (CM)"},
    domain = {'row': 0, 'column': 0}))


fig_indicator.add_trace(go.Indicator(
    mode = "number+delta",
    value = avg_distance_latest_date,
    delta = {'reference': avg_distance_prior_date},
    title = {'text': "Average Distances (CM) (latest vs prior date)"},
    domain = {'row': 0, 'column': 1}))


fig_indicator.update_layout(
    grid = {'rows': 1, 'columns': 2, 'pattern': "independent"},
    template = {'data' : {'indicator': [{
        'mode' : "number+delta+gauge",
        'delta' : {'reference': 90}}]
                         }})


# Distance over time at the latest date
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y,
            mode='lines',
            name='distances'
))
fig.add_trace(go.Scatter(x=x, y=y_distance_limit,
            mode='lines',
            name='distance threshold'
))

fig.update_layout(
    title="Distances over time (Latest date)",
    xaxis_title = "Date time",
    yaxis_title = "Distances"

)

# Distance over time for all time
fig_distance_all = go.Figure()
fig_distance_all.add_trace(go.Scatter(x=df['date_time'].to_list(), y=df['distances'].to_list(),
            mode='lines',
            name='distances'
))
fig_distance_all.add_trace(go.Scatter(x=df['date_time'].to_list(), y=df['distance_limit'].to_list(),
            mode='lines',
            name='distance threshold'
))

fig_distance_all.update_layout(
    title="Distances over time (All data)",
    xaxis_title = "Date time",
    yaxis_title = "Distances"

)

# create watch duration per day

df = pd.read_sql_query(

    """
    with date_time_diff as (
        select *,
            lag(date_time) over (order by date_time) as prior_date_time,
            TIMESTAMPDIFF(MINUTE,lag(date_time) over (order by date_time),date_time) as date_time_diff,
            date(date_time) as date
        from distance
    )

    ,date_segment as (
        select *,
            right(concat('00' , cast(row_number() over (partition by date order by date_time) as char)), 2) as row_no
        from date_time_diff
        where date_time_diff > 60 
            or prior_date_time is null
    )

    ,date_sessions as (
        select *,
            concat(replace(CAST(date AS char), '-', '_'), '_', row_no) as date_segment_id
        from date_segment
        where date_time <> (select max(date_time) from distance)
    )

    select i.*,
        case when date_segment_id is null 
            then first_value(date_segment_id) over (partition by sessions ORDER BY date_time rows between unbounded preceding and current row)
            else date_segment_id end as date_session_id
    from (
        select a.*,
            b.date_segment_id,
            sum(case when date_segment_id is null then 0 else 1 end) 
              over(order by date_time) as sessions
        from distance a
        left join date_sessions b
        on a.date_time = b.date_time
    ) i
    
    """

,dbConnection)

df_date_range = df.groupby(by='date_session_id', as_index=False).agg({'date_time':['min', 'max']})
df_date_range.columns = ['date_session_id', 'min_date_time', 'max_date_time']
df_date_range['duration'] = df_date_range['max_date_time'] - df_date_range['min_date_time']
df_date_range['hours_duration'] = round(df_date_range['duration']/pd.Timedelta('1 hour'),4)
df_date_range['date'] = df_date_range['min_date_time'].dt.date.astype('datetime64')

hours_duration_sum_latest_date = df_date_range[df_date_range['date'] == latest_date]['hours_duration'].sum()
times_sum_latest_date = df_date_range[df_date_range['date'] == latest_date]['hours_duration'].count()
hours_duration_sum_prior_date = df_date_range[df_date_range['date'] == prior_date]['hours_duration'].sum()


fig_indicator_duration = go.Figure()
fig_indicator_duration.add_trace(go.Indicator(
    value = times_sum_latest_date,
    delta = {'reference': 3},
    gauge = {
        'axis': {'visible': False}},
    title = {'text': "Latest date: No. of times on video watch vs threshold"},
    domain = {'row': 0, 'column': 0}))

fig_indicator_duration.add_trace(go.Indicator(
    mode = "number+delta",
    value = hours_duration_sum_latest_date,
    delta = {'reference': hours_duration_sum_prior_date},
    title = {'text': "Video watching (hours) (latest vs prior date)"},
    domain = {'row': 0, 'column': 1}))

fig_indicator_duration.update_layout(
    grid = {'rows': 1, 'columns': 2, 'pattern': "independent"},
    template = {'data' : {'indicator': [{
        'mode' : "number+delta+gauge",
        'delta' : {'reference': 90}}]
                         }})

app.layout = html.Div(children=[
    html.H1(children='Hello Eric'),

    html.Div(children='''
        Jeffrey's distance to monitors report.
    '''),

    dcc.Graph(
        id='indicator-avg-distance',
        figure=fig_indicator

    ),
    dcc.Graph(
        id='example-graph',
        figure=fig
    ),
    dcc.Graph(
        id='graph1',
        figure=fig_distance_all
    ),
    dcc.Graph(
        id='indicator_duration',
        figure=fig_indicator_duration
    )

])

if __name__ == '__main__':
    app.run_server(debug=True)