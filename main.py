# Import Libraries

import pandas as pd
from datetime import timedelta
import dash
from dash import Dash, dcc, html, dcc, callback, Input, Output
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(message)s')

# Import other Files
import data_preparation as dp
import layout as lo


# Import Dataframes
flight_df, instructor_df = dp.load_data()
flight_df = dp.data_cleanup(flight_df, 'flightlog')
instructor_df = dp.data_cleanup(instructor_df, 'instructorlog')

start_date=flight_df['Date'].min()
end_date=flight_df['Date'].max()

filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)
agg_aircraft_df = dp.aircraft_aggregation(filtered_flight_df)
filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)
agg_instructor_df = dp.instructor_aggregation(filtered_instructor_df)
col_flight_df = list(flight_df)[-3:]
col_agg_pilot_df = list(agg_pilot_df)
col_agg_instructor_df = list(agg_instructor_df)


# Build App
app = Dash(external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=flight_df['Date'].min(),
                    end_date=flight_df['Date'].max(),
                    display_format='DD.MM.YYYY'
                ),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    lo.drawcenterText('Flightlog')
                ], width=8),
                dbc.Col([
                    lo.drawcenterText('Instructorlog')
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.RadioItems(col_flight_df, 'YY-MM-DD', inline=True, id='dateformat_dropdown_x')
                ], width=12)
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='main_flightlog_plot')
                ], width=8),
                dbc.Col([
                    dcc.Graph(id='main_instructorlog_plot')
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    lo.drawcenterText('Pilots')
                ], width=8),
                dbc.Col([
                    lo.drawcenterText('Instructors')
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.RadioItems(col_agg_pilot_df, 'Total_Flight_Time', inline=True, id='pilot_dropdown_y'),
                    dcc.Graph(id='main_pilot_plot')
                ], width=8),
                dbc.Col([
                    dcc.RadioItems(col_agg_instructor_df, 'Total_Duration', inline=True, id='instructor_dropdown_y'),
                    dcc.Graph(id='main_instructor_plot')
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='aircraft_plot')
                ], width=4),
                dbc.Col([
                    lo.drawcenterText('Flightlog')
                ], width=4),
            ], align='center'),
        ]), color = 'dark'
    )
])


# Callback for updating the graphs
@app.callback(
    [Output('main_flightlog_plot', 'figure'),
     Output('main_instructorlog_plot', 'figure'),
     Output('main_pilot_plot', 'figure'),
     Output('main_instructor_plot', 'figure'),
     Output('aircraft_plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('dateformat_dropdown_x', 'value'),
     Input('pilot_dropdown_y', 'value'),
     Input('instructor_dropdown_y', 'value')]
)
def update_graphs(start_date, end_date, dateformat_dropdown_x_value, pilot_dropdown_y_value, instructor_dropdown_y):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    # Aggregate on Date
    grouped_flight_df = dp.date_aggregation(filtered_flight_df, dateformat_dropdown_x_value)
    # Create Main Flightlog Plot
    main_flightlog_plot = px.bar(grouped_flight_df, dateformat_dropdown_x_value, 'Flight Time', color='Flight Time',
                  template='plotly_dark')

    # Filter Instructorlog data based on the selected date range
    filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)
    grouped_instructor_df = dp.date_aggregation(filtered_instructor_df, dateformat_dropdown_x_value)
    # Create Main Instructorlog Plot
    main_instructorlog_plot = px.bar(grouped_instructor_df, dateformat_dropdown_x_value, 'Duration', color='Duration',
                  template='plotly_dark')

    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df, pilot_dropdown_y_value)
    # Create Pilot Plot
    main_pilot_plot = px.bar(agg_pilot_df, 'Pilot', pilot_dropdown_y_value, color=pilot_dropdown_y_value, template='plotly_dark')

    # Aggregate Insturctor Data
    agg_instructor_df = dp.instructor_aggregation(filtered_instructor_df, instructor_dropdown_y)
    # Create Instructor Plot
    main_instructor_plot = px.bar(agg_instructor_df, 'Instructor', instructor_dropdown_y, color=instructor_dropdown_y, template='plotly_dark')

    # Aggregate Aircraft Data
    agg_aircraft_df = dp.aircraft_aggregation(filtered_flight_df)
    # Create AIrcraft Plot
    aircraft_plot = px.line(agg_aircraft_df, "Aircraft", "Total_Flight_Time", color="Total_Flight_Time", template='plotly_dark')

    return main_flightlog_plot, main_instructorlog_plot, main_pilot_plot, main_instructor_plot, aircraft_plot

# Run app and display result inline in the notebook
app.run_server()