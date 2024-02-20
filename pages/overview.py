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
import plot

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
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flights"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Number-of-Flights'),
            ]
        )
        ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Landings"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Sum-Landings'),
            ]
        )
        ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Fuel used"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Sum-Fuel'),
            ]
        )
        ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instruction Sets"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Sum-Instruction-Sets'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Trainees"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Sum-Trainees'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instructions Hours"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Instructions-Hours'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_2),

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
        ], **globals.adaptiv_width_6),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instruction Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='main-instructor-plot'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_6)
    ], className="g-0")
])


@callback(
    [Output('Flight-Hours', 'children'),
     Output('Number-of-Flights', 'children'),
     Output('Sum-Landings', 'children'),
     Output('Sum-Fuel', 'children')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_hours(flightlog_dict, start_date, end_date):
    if flightlog_dict is None:
        sum_total, sum_flight_str, sum_landings, sum_fuel = ('NO DATA',) * 4
        return [sum_total, sum_flight_str, sum_landings, sum_fuel]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    # Sum of Flighttime
    sum_total = dp.sum_time_per_Column(filtered_flight_df, None, 'Flight Time')

    # Sum of Flights
    sum_flight = len(filtered_flight_df)
    sum_flight_str = f'{sum_flight} #'

    # Sum of Landings
    sum_landings = f'{filtered_flight_df["Landings"].sum():.0f} #'
    # Sum of Fuel
    sum_fuel = f'{filtered_flight_df["Fuel"].sum():.0f} L'


    return [sum_total, sum_flight_str, sum_landings, sum_fuel]


@callback(
    [Output('Instructions-Hours', 'children'),
     Output('Sum-Trainees', 'children'),
     Output('Sum-Instruction-Sets', 'children')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_flight_hours(instructorlog_dict, start_date, end_date):
    if instructorlog_dict is None:
        sum_instructor_hours, sum_trainees, sum_instruction_sets = ('NO DATA',) * 3
        return [sum_instructor_hours, sum_trainees, sum_instruction_sets]
    # Reload Dataframe from Dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    sum_instructor_hours = dp.sum_time_per_Column(filtered_instructor_df, None, 'Duration')

    sum_trainees = filtered_instructor_df['Pilot'].nunique()
    sum_trainees = f'{sum_trainees:.0f} #'

    sum_instruction_sets = len(filtered_instructor_df)
    sum_instruction_sets = f'{sum_instruction_sets:.0f} #'

    return [sum_instructor_hours, sum_trainees, sum_instruction_sets]


@callback(
    [Output('main-flight-plot', 'figure')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),]
)
def update_flight_graphs(flightlog_dict, start_date, end_date):
    if flightlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

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
def update_instructor_graphs(instructorlog_dict, start_date, end_date):
    if instructorlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # Reload Dataframe from Dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

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
