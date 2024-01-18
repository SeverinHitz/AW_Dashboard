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
import globals

globals.init()

member_path = '231230_members.xlsx'
member_df = dp.load_data(member_path)
member_df = dp.data_cleanup_member(member_df)

dash.register_page(__name__, path='/member', name='Member')


layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Total Members"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Number-of-Members'),
            ]
        )
        ])
        ], width=3),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Members with Status Active"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Member-Status-Active'),
            ]
        )
        ])
        ], width=3),
        dbc.Col([
            dbc.Card([dbc.CardHeader("New in selected Timerange"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='New-in-Timerange'),
                          ]
                      )
                      ])
        ], width=3),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Mean Age of Active Members"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Mean-Age-of-Active-Members'),
                          ]
                      )
                      ])
        ], width=3),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Age Distribution Active Members"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Age-Distribution-Active-Members'),
                          ]
                      )
                      ])
        ], width=4),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Admission new Active Members"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Admission-new-Active-Members'),
                          ]
                      )
                      ])
        ], width=4),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Place of Residence Activ Members"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Place-of-Residence-Activ-Members'),
                          ]
                      )
                      ])
        ], width=4)
    ], className="g-0")
])

