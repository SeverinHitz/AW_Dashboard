# Pilot page

# Libraries
from icecream import ic
import dash
from dash import Dash, dcc, html, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
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
legend = dict(yanchor="top", y=0.99, xanchor="left", x=0.01)

# Path
flightlog_file = '240113_flightlog.xlsx'
instructorlog_file = '240113_instructorlog.xlsx'
reservationlog_file = '240113_reservationlog.xlsx'

# Import Dataframes
flight_df = dp.load_data(flightlog_file)
instructor_df = dp.load_data(instructorlog_file)
reservation_df = dp.load_data(reservationlog_file)

# clean up
flight_df = dp.data_cleanup_flightlog(flight_df)
instructor_df = dp.data_cleanup_instructorlog(instructor_df)
reservation_df = dp.data_cleanup_reservation(reservation_df)

pilots = flight_df['Pilot'].sort_values().unique()


dash.register_page(__name__, path='/pilots', name='Pilots')

layout = html.Div([
    dbc.Row([
        dcc.Dropdown(pilots, 'Severin Hitz', id='Pilot-Dropdown')
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
                              dcc.Graph(id='res1'),
                          ]
                      )
                      ])
        ], width=6),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instruction Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='res2'),
                          ]
                      )
                      ])
        ], width=6)
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

    agg_pilot_reservation = agg_reservation_df[agg_reservation_df['Pilot']==pilot_dropdown]
    agg_pilot_flight = agg_pilot_df[agg_pilot_df['Pilot']==pilot_dropdown]
    str = f'XYZ'

    agg_flight_res_df = dp.reservation_flight_merge(agg_pilot_reservation, agg_pilot_flight)

    if len(agg_flight_res_df)==1:
        # Pilots Flight Time
        sum_flight_time = f'{agg_flight_res_df.iloc[0]["Total_Flight_Time"]:.2f} h'
        # Pilots Number of Flights
        sum_block_time = f'{agg_flight_res_df.iloc[0]['Number_of_Flights']:.2f} h'
        # Pilots Flight to Block Time
        flight_block_ratio = f'{agg_flight_res_df.iloc[0]['Flight_Block_Ratio']*100:.2f} %'
        # Pilots Number of Flights
        sum_flights = f'{agg_flight_res_df.iloc[0]['Number_of_Flights']:.2f} #'
        # Pilots Landings
        sum_landings = f'{agg_flight_res_df.iloc[0]['Number_of_Landings']:.2f} #'
        # Pilots Reservations to Flighttime
        res_flight_time = f'{agg_flight_res_df.iloc[0]['Flight_to_Reservation_Time']*100:.2f} %'
        # Pilots Cancelled Reservation
        reservations = f'{agg_flight_res_df.iloc[0]['Reservations']:.2f} #'
        # Pilots Cancelled Reservation
        cancelled = f'{agg_flight_res_df.iloc[0]['Cancelled']:.2f} #'
        # Pilots Cancelled Ratio
        cancelled_ratio = f'{agg_flight_res_df.iloc[0]['Ratio_Cancelled']*100:.2f} %'
    else:
        pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio, \
            sum_flights, sum_landings, res_flight_time, reservations, cancelled, cancelled_ratio = ('NO DATA',) * 10



    return pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio, sum_flights, sum_landings, res_flight_time, reservations, cancelled, cancelled_ratio


