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
    """
,dbConnection)

df = data_processing(df)

latest_date = max(df['date'])
df_latest_date = df[df['date'] == latest_date]
x = df_latest_date['date_time'].to_list()
y = df_latest_date['distances'].to_list()
y_distance_limit = df_latest_date['distance_limit'].to_list()

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y,
            mode='lines',
            name='distances'
))
fig.add_trace(go.Scatter(x=x, y=y_distance_limit,
            mode='lines',
            name='distance limits'
))

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application for distances data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)