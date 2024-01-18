# Pilot page

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

pilots = flight_df['Pilot'].sort_values().unique()
# Append '⌀ All Pilots' to the array of unique pilot names
pilots = np.append(pilots, '⌀ All Pilots')

dash.register_page(__name__, path='/pilot', name='Pilot')

layout = html.Div([
    dbc.Row([
        dcc.Dropdown(pilots, '⌀ All Pilots', id='Pilot-Dropdown')
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Pilot"),
            dbc.CardBody(
            [
                html.H4("Name", id='Pilot-Name'),
            ]
        )
        ])
        ], width=3),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Pilot-Flight-Hours'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Block Time"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Block-Hours'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flt./Blckt."),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Flight-Block-Time'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flights"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Pilot-Number-of-Flights'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Landings"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Pilot-Number-of-Landings'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flt/Res"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Res-to-Flight-Time'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Reservations"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Pilot-Reservation'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Cancelled"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Pilot-Cancelled'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Canc. Ratio"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Cancelled-Ratio'),
                          ]
                      )
                      ])
        ], width=1)
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Pilots-Flight-Time-Plot'),
                          ]
                      )
                      ])
        ], width=8),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Cancellation Reason"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Pilot-Cancel-Reason'),
                          ]
                      )
                      ])
        ], width=4)
    ], className="g-0")
])


@callback(
    [Output('Pilot-Name', 'children'),
     Output('Pilot-Flight-Hours', 'children'),
     Output('Pilot-Block-Hours', 'children'),
     Output('Pilot-Flight-Block-Time', 'children'),
     Output('Pilot-Number-of-Flights', 'children'),
     Output('Pilot-Number-of-Landings', 'children'),
     Output('Pilot-Res-to-Flight-Time', 'children'),
     Output('Pilot-Reservation', 'children'),
     Output('Pilot-Cancelled', 'children'),
     Output('Pilot-Cancelled-Ratio', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_pilots_header(start_date, end_date, pilot_dropdown):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter Reservation data based on the selected date range
    filtered_reservation_df = dp.date_select_df(reservation_df, start_date, end_date, date_column='From')
    reservation_sum = filtered_reservation_df[filtered_reservation_df['Deleted']]['Deletion Reason'].value_counts()
    agg_reservation_df = dp.reservation_aggregation(filtered_reservation_df)
    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)

    agg_flight_res_df = dp.reservation_flight_merge(agg_reservation_df, agg_pilot_df)
    if pilot_dropdown == '⌀ All Pilots':
        agg_flight_res_df = agg_flight_res_df.iloc[:, 1:].mean().to_frame().T
    else:
        agg_flight_res_df = agg_flight_res_df[agg_flight_res_df['Pilot']==pilot_dropdown]

    if len(agg_flight_res_df)==1:
        # Pilots Flight Time
        sum_flight_time = f'{agg_flight_res_df.iloc[0]["Total_Flight_Time"]:.1f} h'
        # Pilots Number of Flights
        sum_block_time = f'{agg_flight_res_df.iloc[0]['Total_Block_Time']:.1f} h'
        # Pilots Flight to Block Time
        flight_block_ratio = f'{agg_flight_res_df.iloc[0]['Flight_Block_Ratio']*100:.2f} %'
        # Pilots Number of Flights
        sum_flights = f'{agg_flight_res_df.iloc[0]['Number_of_Flights']:.0f} #'
        # Pilots Landings
        sum_landings = f'{agg_flight_res_df.iloc[0]['Number_of_Landings']:.0f} #'
        # Pilots Reservations to Flighttime
        res_flight_time = f'{agg_flight_res_df.iloc[0]['Flight_to_Reservation_Time']*100:.2f} %'
        # Pilots Cancelled Reservation
        reservations = f'{agg_flight_res_df.iloc[0]['Reservations']:.0f} #'
        # Pilots Cancelled Reservation
        cancelled = f'{agg_flight_res_df.iloc[0]['Cancelled']:.0f} #'
        # Pilots Cancelled Ratio
        cancelled_ratio = f'{agg_flight_res_df.iloc[0]['Ratio_Cancelled']*100:.2f} %'
    else:
        pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio, \
            sum_flights, sum_landings, res_flight_time, reservations, cancelled, cancelled_ratio = ('NO DATA',) * 10

    return pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio,\
        sum_flights, sum_landings, res_flight_time, reservations, cancelled, cancelled_ratio


@callback(
    [Output('Pilots-Flight-Time-Plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_pilot_graphs(start_date, end_date, pilot_dropdown):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)
    # Create Pilot Plot
    pilots_flight_time_plot = px.bar(
        agg_pilot_df,
        'Pilot',
        'Total_Flight_Time',
        color='Total_Flight_Time',
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale
    )
    # Update the color of the selected pilot in the bar plot
    if pilot_dropdown != '⌀ All Pilots':
        pilots_flight_time_plot.update_traces(
            marker=dict(color=[globals.discrete_teal[-1] if pilot == pilot_dropdown else globals.discrete_teal[0] for pilot in agg_pilot_df['Pilot']]),
            hovertext=agg_pilot_df['Total_Flight_Time'],
            selector=dict(type='bar')
        )
    pilots_flight_time_plot.update(layout_coloraxis_showscale=False)
    pilots_flight_time_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    pilots_flight_time_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)

    return [pilots_flight_time_plot]

@callback(
    [Output('Pilot-Cancel-Reason', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_reservation_graph(start_date, end_date, pilot_dropdown):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter Reservation data based on the selected date range
    filtered_reservation_df = dp.date_select_df(reservation_df, start_date, end_date, date_column='From')
    if pilot_dropdown != '⌀ All Pilots':
        filtered_reservation_df = filtered_reservation_df[filtered_reservation_df['Pilot']==pilot_dropdown]
    reservation_sum = filtered_reservation_df[filtered_reservation_df['Deleted']]['Deletion Reason'].value_counts()

    # Create Reservation Plot
    pilot_cancel_reason_plot = px.pie(
        reservation_sum,
        names=reservation_sum.index,
        values='count',
        template=globals.plot_template,
        color_discrete_sequence=globals.discrete_teal
    )
    pilot_cancel_reason_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    pilot_cancel_reason_plot.update_layout(margin=globals.plot_margin,
                                       paper_bgcolor=globals.paper_bgcolor,
                                       plot_bgcolor=globals.paper_bgcolor,
                                       legend=globals.legend)

    return [pilot_cancel_reason_plot]

