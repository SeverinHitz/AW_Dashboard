# Intro page

# Libraries
from icecream import ic  # Debugging library for printing variable values
import dash   # Core Dash library
from dash import Dash, dcc, html, callback, Input, Output, dash_table  # Dash components for building
import dash_bootstrap_components as dbc  # Dash components styled with Bootstrap
import pandas as pd  # Data manipulation library
import plotly.express as px  # Library for handling dates and times
# Import other Files
import data_preparation as dp  # Custom module for data preparation tasks
import globals  # Custom module for global variables and settings
import plot

globals.init()  # Initialize global variables

dash.register_page(__name__, path='/overview', name='Overview')  # Page Setup

layout = html.Div([
    # First Row with KPI
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
    # First Row with Graphs
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


# Callback that handles the KPI from the Flightlog
@callback(
    [Output('Flight-Hours', 'children'),  # KPI Flighthours
     Output('Number-of-Flights', 'children'),  # KPI Number of Flights
     Output('Sum-Landings', 'children'),  # KPI Sum Landings
     Output('Sum-Fuel', 'children')],  # KPI Sum Fuel
    [Input('flightlog-store', 'data'),  # Flightlog Data Dict
     Input('date-picker-range', 'start_date'),  # Selected Start Date
     Input('date-picker-range', 'end_date')]  # Selected End Date
)
def update_flight_hours(flightlog_dict, start_date, end_date):
    if flightlog_dict is None:  # If no Flightlog is given
        sum_total, sum_flight_str, sum_landings, sum_fuel = ('NO DATA',) * 4
        return [sum_total, sum_flight_str, sum_landings, sum_fuel]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    # Sum of Flighttime per Column (return is direct a String)
    sum_total = dp.sum_time_per_Column(filtered_flight_df, None, 'Flight Time')

    # Sum of Flights
    sum_flight = len(filtered_flight_df)
    sum_flight_str = f'{sum_flight} #'

    # Sum of Landings
    sum_landings = f'{filtered_flight_df["Landings"].sum():.0f} #'
    # Sum of Fuel
    sum_fuel = f'{filtered_flight_df["Fuel"].sum():.0f} L'


    return [sum_total, sum_flight_str, sum_landings, sum_fuel]

# Callback that handles the KPI from the Instructor Log
@callback(
    [Output('Instructions-Hours', 'children'),  # KPI Instruction Hours
     Output('Sum-Trainees', 'children'),  # KPI SUM Trainees
     Output('Sum-Instruction-Sets', 'children')],  # KPI Sum Instruction Sets
    [Input('instructorlog-store', 'data'),  # Instructorlog Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Datepicker
     Input('date-picker-range', 'end_date')]  # End Date form Datepicker
)
def update_flight_hours(instructorlog_dict, start_date, end_date):
    if instructorlog_dict is None:  # If no Instructorlog Data is available
        sum_instructor_hours, sum_trainees, sum_instruction_sets = ('NO DATA',) * 3
        return [sum_instructor_hours, sum_trainees, sum_instruction_sets]
    # Reload Dataframe from Dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    # Sum Instructor Hours (Function returns direct String)
    sum_instructor_hours = dp.sum_time_per_Column(filtered_instructor_df, None, 'Duration')

    # Sum of Trainees
    sum_trainees = filtered_instructor_df['Pilot'].nunique()
    sum_trainees = f'{sum_trainees:.0f} #'

    # Sum of Instruction Sets
    sum_instruction_sets = len(filtered_instructor_df)
    sum_instruction_sets = f'{sum_instruction_sets:.0f} #'

    return [sum_instructor_hours, sum_trainees, sum_instruction_sets]

# Callback that handles the Main Flight Plot
@callback(
    [Output('main-flight-plot', 'figure')],  # Main Flight Plot
    [Input('flightlog-store', 'data'),  # Flight log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Datepicker
     Input('date-picker-range', 'end_date'),]  # End Date from Datepicker
)
def update_flight_graphs(flightlog_dict, start_date, end_date):
    if flightlog_dict is None:  # If no Flightlog is given
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    # Aggregate Data
    filled_flight_df = dp.agg_by_Day(filtered_flight_df,  # Data
                                         date_column='Date',  # Aggregate by
                                         group_column='Aircraft',  # Group by
                                         agg_column='Flight Time',  # Agg by
                                         out_column='Daily_Flight_Time')  # Name Out Column
    # Create Pilot Plot
    main_flight_plot = px.bar(
        filled_flight_df,  # Data
        'Date',  # x Data
        'Daily_Flight_Time',  # y Data
        color='Aircraft',  # Color by
        template=globals.plot_template,  # Plot template
        color_discrete_sequence=globals.discrete_teal  # Color Range
    )
    main_flight_plot.update_yaxes(showgrid=False)  # Disable Grid
    main_flight_plot.update_layout(margin=globals.plot_margin,  # Plot Margin
                                   paper_bgcolor=globals.paper_bgcolor,  # Paper Background Color
                                   plot_bgcolor=globals.paper_bgcolor,  # Plot Background Color
                                   legend=globals.legend)  # Legend Styling

    return [main_flight_plot]

# Callback that handles the Instructor Figure
@callback(
    [Output('main-instructor-plot', 'figure')],  # Instructor Figure
    [Input('instructorlog-store', 'data'),  # Instructor Log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Date Picker
     Input('date-picker-range', 'end_date')]  # End Date from Date Picker
)
def update_instructor_graphs(instructorlog_dict, start_date, end_date):
    if instructorlog_dict is None:  # If the Instructorlog is not available
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # Reload Dataframe from Dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    # Aggregate Dataframe
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
