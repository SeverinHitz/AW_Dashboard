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

agg_pilot_df = dp.pilot_aggregation(flight_df, start_date, end_date)
agg_instructor_df = dp.instructor_aggregation(instructor_df, start_date, end_date)
agg_aircraft_df = dp.aircraft_aggregation(flight_df, start_date, end_date)
col_agg_pilot_df = list(agg_pilot_df)

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
                    display_format='YYYY-MM-DD'
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
                    dcc.Dropdown(col_agg_pilot_df, 'Pilot', id='pilot_dropdown_x'),
                    dcc.Dropdown(col_agg_pilot_df, 'Total_Flight_Time', id='pilot_dropdown_y'),
                    dcc.Graph(id='main_flightlog_plot')
                ], width=8),
                dbc.Col([
                    dcc.Graph(id='main_instructorlog_plot')
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
     Output('aircraft_plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('pilot_dropdown_x', 'value'),
     Input('pilot_dropdown_y', 'value')]
)
def update_graphs(start_date, end_date, pilot_dropdown_x_value, pilot_dropdown_y_value):
    print('X-Selection: ', pilot_dropdown_x_value)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter data based on the selected date range
    agg_pilot_df = dp.pilot_aggregation(flight_df, start_date, end_date, pilot_dropdown_y_value)
    agg_instructor_df = dp.instructor_aggregation(instructor_df, start_date, end_date)
    agg_aircraft_df = dp.aircraft_aggregation(flight_df, start_date, end_date)
    # Create plots
    fig1 = px.bar(agg_pilot_df, pilot_dropdown_x_value, pilot_dropdown_y_value)
    fig2 = px.bar(agg_instructor_df, "Instructor", "Total_Instructor_Time")
    fig3 = px.bar(agg_aircraft_df, "Aircraft", "Total_Flight_Time")

    return fig1, fig2, fig3


# Run app and display result inline in the notebook
app.run_server()