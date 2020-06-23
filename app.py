import pandas as pd
from datetime import datetime as dt
from datetime import timedelta

import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
from dash.dependencies import Input, Output, State

# set up app
app = dash.Dash(__name__)

# Set server
server = app.server

# mapbox secret token
token = 'pk.eyJ1IjoiZWNvcm9uYWRvOTIiLCJhIjoiY2tibnY1YTQ2MXd0MDJ5bnpkZHdkcHM3cCJ9.EbmklfwT4KGmUWqnDL6Wwg'

# Read data and pivot longer to be able to use plot colors per hospital
df = pd.read_csv('https://raw.githubusercontent.com/diegomatuk/MIT_Covid19/master/data.csv')

df_melt = df.melt(id_vars=['Name', 'Place_id', 'Latitude', 'Longitude', 'Type'],
                  var_name='date', value_name='current_count')

# Add machine capacity column
df_melt['machine_capacity'] = 100
df_melt['current_remain_perc'] = df_melt['current_count']/100 # turn into frequencies

hospital_names = df.Name.unique()


# Layout
app.layout = html.Div(children=[
                      html.Div(className='row',
                               children=[
                                  # Left panel
                                  html.Div(className='four columns div-user-controls',
                                          children=[
                                              html.Img(className='logo',src=app.get_asset_url("covending_logo2.png")),

                                              # Actualizacion del mapa
                                              html.H2('Búsqueda de suministros por fecha'),
                                              html.P("Seleccione fecha inicial"),
                                              dcc.DatePickerSingle(
                                                  id='map-date',
                                                  min_date_allowed=dt(2020, 4, 22),
                                                  max_date_allowed=dt(2020, 6, 20),
                                                  initial_visible_month=dt(2020, 6, 20).date() ,
                                                  date=dt(2020, 6, 20).date(),
                                                  display_format='DD/MM/Y',
                                                  month_format='MMM Do, YYYY'),
                                              html.P("* simulated data")

                                              html.Br(),
                                              html.Br(),
                                              html.Br(),
                                              html.Div(children=[
                                                   html.H6('Información importante'),
                                                   html.Img(className='infographic',src=app.get_asset_url("n95Diagrama2.png"))
                                              ])

                                          ]),

                                   # Chart panel
                                  html.Div(className='eight columns div-for-charts bg-grey',
                                          children=[
                                              # Map
                                              html.H2('Abastecimiento de hospitales en la ciudad de Lima'),
                                              dcc.Graph(id='map-scatter', # build a blank graph at start
                                                        figure={
                                                            'data': [],
                                                            'layout': go.Layout(
                                                                xaxis={
                                                                    'showticklabels': False,
                                                                    'ticks': '',
                                                                    'showgrid': False,
                                                                    'zeroline': False},
                                                                yaxis={
                                                                    'showticklabels': False,
                                                                    'ticks': '',
                                                                    'showgrid': False,
                                                                    'zeroline': False},
                                                            )}
                                                       ),

                                              # Trendline charts
                                              html.H2('Tendencias de abastecimiento'),
                                              dcc.DatePickerRange(
                                                  id="date-query",
                                                  display_format='D/MM/Y',
                                                  month_format='MMM Do, YYYY',
                                                  min_date_allowed=dt(2020, 4, 22),
                                                  max_date_allowed=dt(2020, 6, 21),
                                                  start_date=dt(2020, 4, 22).date(),
                                                  end_date = dt(2020, 6, 20).date()
                                              ),
                                              html.Br(),
                                              dcc.Dropdown(id='dropdown',
                                                           options=[{'label': i, 'value': i} for i in hospital_names],
                                                           multi=True,
                                                           placeholder='Filtrar hospitales...'),

                                              dcc.Graph(id='map-trends', # same as above, blank chart
                                                        figure={
                                                            'data': [],
                                                            'layout': go.Layout(
                                                                xaxis={
                                                                    'showticklabels': False,
                                                                    'ticks': '',
                                                                    'showgrid': False,
                                                                    'zeroline': False},
                                                                yaxis={
                                                                    'showticklabels': False,
                                                                    'ticks': '',
                                                                    'showgrid': False,
                                                                    'zeroline': False},

                                                            )}
                                                       ),
                                            html.H2('Optimización de Rutas'),
                                            html.Iframe(id = 'mapa1', 
                                                        srcDoc = open('folium.html','r').read(),
                                                        height = '600',
                                                        style = {'margin':'2px'}),
                                          ])
                               ])
])



# Callbacks
@app.callback(
    Output('map-scatter', 'figure'),
    [Input('map-date', 'date')]
)
def update_map(map_date):
    '''Update map based on date selected'''

    # Filter for selected date
    df_sub = df_melt[df_melt['date'] == map_date]

    # Plot and update layout
    fig = px.scatter_mapbox(df_sub, lat="Latitude", lon="Longitude", zoom=11, color='current_remain_perc',
                            hover_name='Name',
                            hover_data=['Type', 'machine_capacity','current_count', 'current_remain_perc'])

    fig.update_traces(overwrite=True,
                      marker=dict(size=12,
                                  color=df_sub['current_remain_perc'],
                                  opacity=0.8,
                                  colorscale=[[0, "#cc3232"],
                                              [0.30, "#e7b416"],
                                              [0.50, "#e7b416"],
                                              [1.0, "#2dc937"]])

                     )

    fig.update_layout(mapbox_accesstoken=token, # important for mapbox
                      mapbox_style='dark',
                      plot_bgcolor= 'rgba(0, 0, 0, 0)',
                      paper_bgcolor= 'rgba(0, 0, 0, 0)',
                     showlegend=False, height=450,
                     margin=go.layout.Margin(l=0, r=0, t=0, b=0))

    return fig




@app.callback(
    Output('map-trends', 'figure'),
    [Input('date-query', 'start_date'),
    Input('date-query', 'end_date'),
    Input('dropdown', 'value')]
)
def update_trends(start_date, end_date, dropdown_value):
    '''Update trendlines based on date range and selected hospital'''

    # Filter for dates
    df_sub = df_melt[(df_melt['date'] >= start_date) & (df_melt['date']<= end_date)]

    # Plot first hospital at start, when selected plot whatever is selected
    if dropdown_value is None:
        df_sub1 = df_sub[df_sub.Name.str.contains(hospital_names[0])]
    else:
        df_sub1 = df_sub[df_sub.Name.str.contains('|'.join(dropdown_value))]

    # Plot trendlines
    fig2 = px.line(df_sub1, x='date', y ='current_count', color='Name')

    # Update layout
    fig2.update_layout(plot_bgcolor= 'rgba(0, 0, 0, 0)',
                      paper_bgcolor= 'rgba(0, 0, 0, 0)',
                      uniformtext_minsize=12,
                      legend=dict(font_family='Helvetica Neue', font_color='#FFF', title="Hospital"),
                      font_color='#FFF',
                      xaxis_title="Fechas",
                      yaxis_title="Abastecimiento",)
    fig2.update_xaxes(title_font=dict(size=18, family='Helvetica Neue', color='#FFF'))
    fig2.update_yaxes(title_font=dict(size=18, family='Helvetica Neue', color='#FFF'))

    return fig2


# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
