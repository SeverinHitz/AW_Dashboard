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
import plot as plots
import data_preparation as dp
import globals
import plot

globals.init()


# Geographical data
# Path
gemeinde_path = 'PLZO_PLZ.shp'
# Import
gem_gdf = dp.load_geodata(gemeinde_path)
# Cleanup
gem_gdf = dp.data_cleanup_gem_df(gem_gdf)

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
            dbc.Card([dbc.CardHeader("New Activ Members in selected Timerange"),
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


@callback(
    [Output('Number-of-Members', 'children'),
     Output('Member-Status-Active', 'children'),
     Output('New-in-Timerange', 'children'),
     Output('Mean-Age-of-Active-Members', 'children')],
    [Input('member-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_member_header(member_dict, start_date, end_date):
    if member_dict is None:
        total_members, active_members, new_members_in_timerange, mean_age_active_members = ('NO DATA',) * 4
        return total_members, active_members, new_members_in_timerange, mean_age_active_members
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Reload Data from Dict
    member_df = dp.reload_member_dataframe_from_dict(member_dict)

    agg_member_df = dp.member_aggregation(member_df)

    # Count all Members
    total_members = f'{len(member_df)} #'

    # Count all active Members
    active_members = f"{len(member_df[member_df['Membership']=='Aktiv'])} #"

    # Select new Members in Timerange
    in_timerange_df = agg_member_df[(agg_member_df['Join Date'] >= start_date) &\
                                    (agg_member_df['Join Date'] <= end_date)]
    new_members_in_timerange = f'{len(in_timerange_df[in_timerange_df['Membership']=='Aktiv'])} #'

    # Mean Age of active members
    mean_age_active_members = f"{agg_member_df[agg_member_df['Membership']=='Aktiv']['Age'].mean():.1f} J"

    return total_members, active_members, new_members_in_timerange, mean_age_active_members

@callback(
    [Output('Age-Distribution-Active-Members', 'figure'),
     Output('Admission-new-Active-Members', 'figure'),
     Output('Place-of-Residence-Activ-Members', 'figure')],
    [Input('member-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_member_graph(member_dict, start_date, end_date):
    if member_dict is None:
        not_data_plot = plot.not_data_figure()
        return not_data_plot, not_data_plot, not_data_plot
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Reload Data from Dict
    member_df = dp.reload_member_dataframe_from_dict(member_dict)

    agg_member_df = dp.member_aggregation(member_df)
    agg_member_df = agg_member_df[agg_member_df['Membership']=='Aktiv']

    member_age_dist_plot = plots.member_histogram(agg_member_df)

    member_join_plot = plots.memeber_join_linegraph(agg_member_df)

    member_location_plot = plots.member_location_graph(agg_member_df, gem_gdf)

    return member_age_dist_plot, member_join_plot, member_location_plot
