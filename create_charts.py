# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import numpy as np

def data_processing(input: pd.DataFrame) -> pd.DataFrame:

    input['date'] = input['date_time'].dt.date.astype('datetime64')
    input['distances'] = round(df['distances'],2)
    return input

app = dash.Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

sqlEngine = create_engine('mysql+pymysql://root:@127.0.0.1/face_to_monitor_distance', \
                        pool_recycle=3600)
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

df

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
    )

])

if __name__ == '__main__':
    app.run_server(debug=True)