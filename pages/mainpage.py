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

# Import Dataframes
flight_df = dp.load_data(flightlog_file)
instructor_df = dp.load_data(instructorlog_file)

# clean up
flight_df = dp.data_cleanup_flightlog(flight_df)
instructor_df = dp.data_cleanup_instructorlog(instructor_df)


dash.register_page(__name__, path='/', name='Main')

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
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_hours(start_date, end_date):
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
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_hours(start_date, end_date):
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
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_graphs(start_date, end_date):
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
        template=plot_template,
        color_discrete_sequence=discrete_teal
    )
    main_flight_plot.update_yaxes(showgrid=False)
    main_flight_plot.update_layout(margin=plot_margin,
                                   paper_bgcolor=paper_bgcolor,
                                   plot_bgcolor=paper_bgcolor,
                                   legend=legend)

    return [main_flight_plot]

@callback(
    [Output('main-instructor-plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_graphs(start_date, end_date):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
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
        'Date',
        'Daily_Instruction_Time',
        color='Instructor',
        template=plot_template,
        color_discrete_sequence=discrete_teal
    )
    main_instructor_plot.update_yaxes(showgrid=False)
    main_instructor_plot.update_layout(margin=plot_margin,
                                       paper_bgcolor=paper_bgcolor,
                                       plot_bgcolor=paper_bgcolor,
                                       legend=legend)

    return [main_instructor_plot]
