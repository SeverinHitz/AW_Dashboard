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
import trend_calculation as tc
import string_func as sf
import globals  # Custom module for global variables and settings
import plot

globals.init()  # Initialize global variables

dash.register_page(__name__, path='/overview', name='Overview')  # Page Setup

layout = html.Div([
    # First Row with KPI
    dcc.Loading(
        id='loading-kpi-overview',
        type='default',
        children=html.Div(
            dbc.Row([
            dbc.Col([
                dbc.Card([dbc.CardHeader("Flight Hours"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Flight-Hours'),
                    html.H6("→ XX %", style={'color': 'grey'}, id='Flight-Hours-Trend')
                ]
            )
            ])
            ], **globals.adaptiv_width_2),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Flights"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Number-of-Flights'),
                    html.H6("→ XX %", style={'color': 'grey'}, id='Number-of-Flights-Trend')
                ]
            )
            ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Landings"),
                dbc.CardBody(
                [
                    html.H4("XXX #", id='Sum-Landings'),
                    html.H6("→ XX %", style={'color': 'grey'}, id='Sum-Landings-Trend')
                ]
            )
            ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Fuel used"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Sum-Fuel'),
                    html.H6("→ XX %", style={'color': 'grey'}, id='Sum-Fuel-Trend')
                ]
            )
            ])
            ], **globals.adaptiv_width_2),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Instruction Sets"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Sum-Instruction-Sets'),
                              html.H6("→ XX %", style={'color': 'grey'}, id='Sum-Instruction-Sets-Trend')
                          ]
                      )
                      ])
            ], **globals.adaptiv_width_2),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Trainees"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Sum-Trainees'),
                              html.H6("→ XX %", style={'color': 'grey'}, id='Sum-Trainees-Trend')
                          ]
                      )
                      ])
            ], **globals.adaptiv_width_2),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Instructions Hours"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Instructions-Hours'),
                              html.H6("→ XX %", style={'color': 'grey'}, id='Instructions-Hours-Trend')
                          ]
                      )
                      ])
            ], **globals.adaptiv_width_2),

        ], className="g-0"))),
    # First Row with Graphs
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-main-flight-plot',
                                  type='cube',
                                  children=html.Div(
                                      dcc.Graph(id='main-flight-plot'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_6),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instruction Time"),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-main-instructor-plot',
                                  type='cube',
                                  children=html.Div(
                                          dcc.Graph(id='main-instructor-plot'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_6)
    ], className="g-0")
])


# Callback that handles the KPI from the Flightlog
@callback(
    [Output('Flight-Hours', 'children'),  # KPI Flighthours
    Output('Flight-Hours-Trend', 'children'),  # KPI Flighthours Trend
     Output('Flight-Hours-Trend', 'style'),  # KPI Flighthours Trend Style

     Output('Number-of-Flights', 'children'),  # KPI Number of Flights
     Output('Number-of-Flights-Trend', 'children'),  # KPI Number of Flights Trend
     Output('Number-of-Flights-Trend', 'style'),  # KPI Number of Flights Trend Style

     Output('Sum-Landings', 'children'),  # KPI Sum Landings
     Output('Sum-Landings-Trend', 'children'),  # KPI Sum Landings Trend
     Output('Sum-Landings-Trend', 'style'),  # KPI Sum Landings Trend Style

     Output('Sum-Fuel', 'children'),  # KPI Sum Fuel
     Output('Sum-Fuel-Trend', 'children'),  # KPI Sum Fuel Trend
     Output('Sum-Fuel-Trend', 'style')],  # KPI Sum Fuel Trend

    [Input('flightlog-store', 'data'),  # Flightlog Data Dict
     Input('date-picker-range', 'start_date'),  # Selected Start Date
     Input('date-picker-range', 'end_date')]  # Selected End Date
)
def update_flight_hours(flightlog_dict, start_date, end_date):
    if flightlog_dict is None:  # If no Flightlog is given
        sum_total, sum_flight, sum_landings, sum_fuel = ('NO DATA',) * 4
        sum_total_trend, sum_flight_trend, sum_landings_trend, sum_fuel_trend = ('trend na',) * 4
        sum_total_trend_style, sum_flight_trend_style, sum_landings_trend_style, sum_fuel_trend_style = ({'color': 'grey'},) * 4
        return [sum_total, sum_total_trend, sum_total_trend_style,
                sum_flight, sum_flight_trend, sum_flight_trend_style,
                sum_landings, sum_landings_trend, sum_landings_trend_style,
                sum_fuel, sum_fuel_trend, sum_fuel_trend_style]

    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    try:  # Try reload of with offset of one year
        # Check if the time difference is over one year
        if abs((pd.Timestamp(start_date) - pd.Timestamp(end_date)).days) > 365:
            raise ValueError("Difference is over a Year.")
        # Reload with offset
        offset = 1  # in years
        filtered_flight_df_trend = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date, offset)
        if len(filtered_flight_df) < 1:
            raise ValueError("Empty Dataframe")
        # Select kpi and select kpi minus offset
        selected, selected_t_minus = tc.select_overview_page_flightlog(filtered_flight_df, filtered_flight_df_trend)
        kpi = sf.trend_string_overview_page_flightlog(selected)
        # Get Return list with trend
        trend_strings, trend_styles = tc.trend_calculation(selected, selected_t_minus)
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    except Exception as e: # If over one year or not possible to load Data
        print(e)
        selected = tc.sum_overview_page_flightlog(filtered_flight_df) # Only the Kpis
        kpi = sf.trend_string_overview_page_flightlog(selected)
        trend_strings, trend_styles = sf.trend_string(len(selected))
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    return return_list


# Callback that handles the KPI from the Instructor Log
@callback(
    [Output('Instructions-Hours', 'children'),  # KPI Instruction Hours
     Output('Instructions-Hours-Trend', 'children'),  # KPI Instruction Hours Trend
     Output('Instructions-Hours-Trend', 'style'),  # KPI Instruction Hours Trend Style

     Output('Sum-Trainees', 'children'),  # KPI SUM Trainees
     Output('Sum-Trainees-Trend', 'children'),  # KPI SUM Trainees Trend
     Output('Sum-Trainees-Trend', 'style'),  # KPI SUM Trainees Trend Style

     Output('Sum-Instruction-Sets', 'children'),  # KPI Sum Instruction Sets
     Output('Sum-Instruction-Sets-Trend', 'children'),  # KPI Sum Instruction Sets Trend
     Output('Sum-Instruction-Sets-Trend', 'style')],  # KPI Sum Instruction Sets Trend Style

    [Input('instructorlog-store', 'data'),  # Instructorlog Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Datepicker
     Input('date-picker-range', 'end_date')]  # End Date form Datepicker
)
def update_flight_hours(instructorlog_dict, start_date, end_date):
    if instructorlog_dict is None:  # If no Instructorlog Data is available
        sum_instructor_hours, sum_trainees, sum_instruction_sets = ('NO DATA',) * 3
        sum_instructor_hours_trend, sum_trainees_trend, sum_instruction_sets_trend = ('trend na',) * 3
        sum_instructor_hours_trend_style, sum_trainees_trend_style, sum_instruction_sets_trend_style = ({'color': 'grey'},) * 3
        return [sum_instructor_hours, sum_instructor_hours_trend, sum_instructor_hours_trend_style,
                sum_trainees, sum_trainees_trend, sum_trainees_trend_style,
                sum_instruction_sets, sum_instruction_sets_trend, sum_instruction_sets_trend_style]

    # reload dataframe form dict
    filtered_flight_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)
    try:  # Try reload of with offset of one year
        # Check if the time difference is over one year
        if abs((pd.Timestamp(start_date) - pd.Timestamp(end_date)).days) > 365:
            raise ValueError("Difference is over a Year.")
        # Reload with offset
        offset = 1  # in years
        filtered_flight_df_trend = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date, offset)
        if len(filtered_flight_df) < 1:
            raise ValueError("Empty Dataframe")
        # Select kpi and select kpi minus offset
        selected, selected_t_minus = tc.select_overview_page_instructorlog(filtered_flight_df, filtered_flight_df_trend)
        kpi = sf.trend_string_overview_page_instructorlog(selected)
        trend_strings, trend_styles = tc.trend_calculation(selected, selected_t_minus)
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    except Exception as e:  # If over one year or not possible to load Data
        print(e)
        selected = tc.sum_overview_page_instructorlog(filtered_flight_df)  # Only the Kpis
        kpi = sf.trend_string_overview_page_instructorlog(selected)
        trend_strings, trend_styles = sf.trend_string(len(selected))
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]


    return return_list

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
