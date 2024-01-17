# Aircraft page

# Libraries
from icecream import ic
import dash
from dash import Dash, dcc, html, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
# Import other Files
import data_preparation as dp
import layout as lo
import plot as plots

# Layout
stylesheet = dbc.themes.SLATE #YETI
layout_color = 'dark' #None
plot_template = 'plotly_dark' #'plotly_white'
color_scale = 'teal'
plot_margin = dict(l=5, r=5, t=15, b=5)
paper_bgcolor = 'rgba(0,0,0,0)'
plot_window_style = { 'border-radius':'5px', 'background-color':'None'}
discrete_teal = ['#2c5977', '#3a718d', '#4f90a6', '#62a5b4', '#7dbdc4', '#8fcacd', '#a1d7d6', '#E4FFFF', '#cfede9']
grid_color = 'lightgrey'
legend = dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor='rgba(255, 255, 255, 0.2)')

# Path
flightlog_file = '240113_flightlog.xlsx'
instructorlog_file = '240113_instructorlog.xlsx'
reservationlog_file = '240113_reservationlog.xlsx'

# Import Dataframes
flight_df = dp.load_data(flightlog_file)
reservation_df = dp.load_data(reservationlog_file)

# clean up
flight_df = dp.data_cleanup_flightlog(flight_df)
reservation_df = dp.data_cleanup_reservation(reservation_df)

pilots = flight_df['Aircraft'].sort_values().unique()
# Append '⌀ All Pilots' to the array of unique pilot names
pilots = np.append(pilots, '⌀ All Aircrafts')

dash.register_page(__name__, path='/aircrafts', name='Aircrafts')


layout = html.Div([
    dbc.Row([
        dcc.Dropdown(pilots, '⌀ All Aircrafts', id='Aircraft-Dropdown')
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Aircaft"),
            dbc.CardBody(
            [
                html.H4("Name", id='Aircraft-Registration'),
            ]
        )
        ])
        ], width=3),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Aircraft-Flight-Hours'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flights"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Aircraft-Number-of-Flights'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("⌀ Flt Time"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Aircraft-Mean-Flight-Time'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Landings"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Aircraft-Number-of-Landings'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Airports"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Aircraft-Number-of-Airports'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Fuel p. h."),
            dbc.CardBody(
            [
                html.H4("XXX L", id='Aircraft-Fuel-per-Hour'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Oil p. h."),
            dbc.CardBody(
            [
                html.H4("XXX mL", id='Oil-per-Hour'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Inst. Ratio"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Aircraft-Instruction-Ratio'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("# Pilots"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Oil-per-Hour'),
            ]
        )
        ])
        ], width=1),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Aircraft-Flight-Time-Plot'),
                          ]
                      )
                      ])
        ], width=4),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Type"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Aircraft-Flight-Type-Plot'),
                          ]
                      )
                      ])
        ], width=4),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Heatmap"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Aircraft-Heatmap'),
                          ]
                      )
                      ])
        ], width=4)
    ], className="g-0")
])
