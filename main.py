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
import html_functions as html_func


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
                    html_func.drawcenterText('Flightlog')
                ], width=8),
                dbc.Col([
                    html_func.drawcenterText('Instructorlog')
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
                    html_func.drawcenterText('Pilots')
                ], width=8),
                dbc.Col([
                    html_func.drawcenterText('Instructors')
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
                    html_func.drawcenterText('Flightlog')
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
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    grouped_flight_df = filtered_flight_df.groupby(dateformat_dropdown_x_value)['Flight Time'].sum().reset_index()
    grouped_flight_df['Flight Time'] = grouped_flight_df['Flight Time'].dt.total_seconds() / 3600
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df, pilot_dropdown_y_value)
    agg_aircraft_df = dp.aircraft_aggregation(filtered_flight_df)
    filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)
    grouped_instructor_df = filtered_instructor_df.groupby(dateformat_dropdown_x_value)['Duration'].sum().reset_index()
    grouped_instructor_df['Duration'] = grouped_instructor_df['Duration'].dt.total_seconds() / 3600
    agg_instructor_df = dp.instructor_aggregation(filtered_instructor_df, instructor_dropdown_y)
    # Create plots
    fig0 = px.bar(grouped_flight_df, dateformat_dropdown_x_value, 'Flight Time', color='Flight Time', template='plotly_dark')
    fig1 = px.bar(grouped_instructor_df, dateformat_dropdown_x_value, 'Duration', color='Duration', template='plotly_dark')
    fig2 = px.bar(agg_pilot_df, 'Pilot', pilot_dropdown_y_value, color=pilot_dropdown_y_value, template='plotly_dark')
    fig3 = px.bar(agg_instructor_df, 'Instructor', instructor_dropdown_y, color='Total_Duration', template='plotly_dark')
    fig4 = px.bar(agg_aircraft_df, "Aircraft", "Total_Flight_Time", color="Total_Flight_Time", template='plotly_dark')

    return fig0, fig1, fig2, fig3, fig4

# Run app and display result inline in the notebook
app.run_server()