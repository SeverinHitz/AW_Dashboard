# Intro page

# Libraries
from icecream import ic
import dash
from dash import Dash, dcc, html, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
# Import other Files
import data_preparation as dp
import globals

globals.init()

dash.register_page(__name__, path='/overview', name='Overview')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Hours"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Flight-Hours'),
            ]
        )
        ])
        ], width=2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flights"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Number-of-Flights'),
            ]
        )
        ])
        ], width=2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("HB-CQW"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='HB-CQW-Hours'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("HB-POX"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='HB-POX-Hours'),
            ]
        )
        ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("HB-SGZ"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='HB-SGZ-Hours'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("HB-SFU"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='HB-SFU-Hours'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("HB-POD"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='HB-POD-Hours'),
                          ]
                      )
                      ])
        ], width=1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instructions Hours"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Instructions-Hours'),
                          ]
                      )
                      ])
        ], width=3),

    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='main-flight-plot'),
                          ]
                      )
                      ])
        ], width=6),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instruction Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='main-instructor-plot'),
                          ]
                      )
                      ])
        ], width=6)
    ], className="g-0")
])


@callback(
    [Output('Flight-Hours', 'children'),
     Output('Number-of-Flights', 'children'),
     Output('HB-CQW-Hours', 'children'),
     Output('HB-POX-Hours', 'children'),
     Output('HB-SGZ-Hours', 'children'),
     Output('HB-SFU-Hours', 'children'),
     Output('HB-POD-Hours', 'children')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_hours(flightlog_dict, start_date, end_date):
    # Load Data from Store
    flight_df = pd.DataFrame.from_dict(flightlog_dict)
    # Convert the 'date_column' to timestamps
    flight_df['Date'] = pd.to_datetime(flight_df['Date'])
    # Set Time as Timedelta
    flight_df['Flight Time'] = pd.to_timedelta(flight_df['Flight Time'].astype(str))
    flight_df['Block Time'] = pd.to_timedelta(flight_df['Block Time'].astype(str))
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)

    # Sum of Flighttime
    sum_total = dp.sum_time_per_Column(filtered_flight_df, None, 'Flight Time')

    # Sum of Flights
    sum_flight = len(filtered_flight_df)
    sum_flight_str = f'{sum_flight} #'

    # Sum Flight Time CQW
    sum_cqw = dp.sum_time_per_Column(filtered_flight_df, 'Aircraft', 'Flight Time','HB-CQW')
    # Sum Flight Time POX
    sum_pox = dp.sum_time_per_Column(filtered_flight_df, 'Aircraft', 'Flight Time', 'HB-POX')
    # Sum Flight Time sgz
    sum_sgz = dp.sum_time_per_Column(filtered_flight_df, 'Aircraft', 'Flight Time', 'HB-SGZ')
    # Sum Flight Time sfu
    sum_sfu = dp.sum_time_per_Column(filtered_flight_df, 'Aircraft', 'Flight Time', 'HB-SFU')
    # Sum Flight Time pod
    sum_pod = dp.sum_time_per_Column(filtered_flight_df, 'Aircraft', 'Flight Time', 'HB-POD')


    return [sum_total, sum_flight_str, sum_cqw, sum_pox, sum_sgz, sum_sfu, sum_pod]


@callback(
    [Output('Instructions-Hours', 'children')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_hours(instructorlog_dict, start_date, end_date):
    # Load Data from Store
    instructor_df = pd.DataFrame.from_dict(instructorlog_dict)
    # Convert the 'date_column' to timestamps
    instructor_df['Date'] = pd.to_datetime(instructor_df['Date'])
    # Set Time as Timedelta
    instructor_df['Duration'] = pd.to_timedelta(instructor_df['Duration'].astype(str))
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter Instructorlog data based on the selected date range
    filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)

    # Sum Flight Time CQW
    sum_instructor_hours = dp.sum_time_per_Column(filtered_instructor_df, None, 'Duration')

    return [sum_instructor_hours]


@callback(
    [Output('main-flight-plot', 'figure')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),]
)
def update_flight_graphs(flightlog_dict, start_date, end_date):
    # Load Data from Store
    flight_df = pd.DataFrame.from_dict(flightlog_dict)
    # Convert the 'date_column' to timestamps
    flight_df['Date'] = pd.to_datetime(flight_df['Date'])

    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    filled_flight_df = dp.agg_by_Day(filtered_flight_df,
                                         date_column='Date',
                                         group_column='Aircraft',
                                         agg_column='Flight Time',
                                         out_column='Daily_Flight_Time')
    # Create Pilot Plot
    main_flight_plot = px.bar(
        filled_flight_df,
        'Date',
        'Daily_Flight_Time',
        color='Aircraft',
        template=globals.plot_template,
        color_discrete_sequence=globals.discrete_teal
    )
    main_flight_plot.update_yaxes(showgrid=False)
    main_flight_plot.update_layout(margin=globals.plot_margin,
                                   paper_bgcolor=globals.paper_bgcolor,
                                   plot_bgcolor=globals.paper_bgcolor,
                                   legend=globals.legend)

    return [main_flight_plot]

@callback(
    [Output('main-instructor-plot', 'figure')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_graphs(instructorlog_dict, start_date, end_date):
    # Load Data from Store
    instructor_df = pd.DataFrame.from_dict(instructorlog_dict)
    # Convert the 'date_column' to timestamps
    instructor_df['Date'] = pd.to_datetime(instructor_df['Date'])

    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    date_bin_size = dp.data_diff_visual_bins(start_date, end_date)
    # Filter Flightlog data based on the selected date range
    filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)
    filled_instructor_df = dp.agg_by_Day(filtered_instructor_df,
                                         date_column='Date',
                                         group_column='Instructor',
                                         agg_column='Duration',
                                         out_column='Daily_Instruction_Time')

    # Create Instructor Plot
    main_instructor_plot = px.bar(
        filled_instructor_df,
        x='Date',
        y='Daily_Instruction_Time',
        color='Instructor',
        template=globals.plot_template,
        color_discrete_sequence=globals.discrete_teal
    )
    main_instructor_plot.update_yaxes(showgrid=False)
    main_instructor_plot.update_layout(margin=globals.plot_margin,
                                       paper_bgcolor=globals.paper_bgcolor,
                                       plot_bgcolor=globals.paper_bgcolor,
                                       legend=globals.legend)

    return [main_instructor_plot]
