# Import Libraries

import pandas as pd
import geopandas as gpd
from datetime import timedelta
import dash
from dash import Dash, dcc, html, dcc, callback, Input, Output, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from icecream import ic
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(message)s')

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

# Import Airmanager Data
# Path
flightlog_file = '240113_flightlog.xlsx'
instructorlog_file = '240113_instructorlog.xlsx'
member_path = '231230_members.xlsx'
reservationlog_file = '240113_reservationlog.xlsx'

# Import Dataframes
flight_df = dp.load_data(flightlog_file)
instructor_df = dp.load_data(instructorlog_file)
member_df = dp.load_data(member_path)
reservation_df = dp.load_data(reservationlog_file)

# clean up
flight_df = dp.data_cleanup_flightlog(flight_df)
instructor_df = dp.data_cleanup_instructorlog(instructor_df)
member_df = dp.data_cleanup_member(member_df)
reservation_df = dp.data_cleanup_reservation(reservation_df)

# Geographical data
# Path
gemeinde_path = 'PLZO_PLZ.shp'
# Import
gem_gdf = dp.load_geodata(gemeinde_path)
# Cleanup
gem_gdf = dp.data_cleanup_gem_df(gem_gdf)


# Data Preparation
# Time select
start_date=reservation_df['From'].min()
end_date=reservation_df['To'].max()
ic(start_date)
ic(end_date)
filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)
filtered_reservation_df = dp.date_select_df(reservation_df, start_date, end_date, date_column='From')

# Aggregate data
agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)
agg_aircraft_df = dp.aircraft_aggregation(filtered_flight_df)
agg_instructor_df = dp.instructor_aggregation(filtered_instructor_df)
agg_reservation_df = dp.reservation_aggregation(filtered_reservation_df)
agg_flight_res_df = dp.reservation_flight_merge(agg_reservation_df, agg_pilot_df)
member_df = dp.member_aggregation(member_df)

# Extract Columns for Selection
col_flight_df = list(flight_df)[-3:]
col_agg_pilot_df = list(agg_pilot_df)
col_agg_instructor_df = list(agg_instructor_df)
col_agg_aircraft_df = list(agg_aircraft_df)
col_agg_flight_res_df = list(agg_flight_res_df)


# Build App
app = Dash(external_stylesheets=[stylesheet])

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4('Select Date')
                ]),
                dbc.Col([
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=reservation_df['From'].min(),
                    end_date=reservation_df['To'].max(),
                    display_format='DD.MM.YYYY'
                ),
            ])
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H2('Flightlog'),
                    html.Hr()
                ], width=8),
                dbc.Col([
                    html.H2('Instructorlog'),
                    html.Hr()
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.RadioItems(col_flight_df, 'YY-MM', inline=True, id='dateformat_dropdown_x',
                                   labelStyle = {'cursor': 'pointer', 'margin-left':'20px'})
                ], width=12)
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='main_flightlog_plot',
                              style=plot_window_style)
                ], width=8),
                dbc.Col([
                    dcc.Graph(id='main_instructorlog_plot')
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H2('Pilots'),
                    html.Hr()
                ], width=8),
                dbc.Col([
                    html.H2('Instructors'),
                    html.Hr()
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.RadioItems(col_agg_pilot_df, 'Total_Flight_Time', inline=True, id='pilot_dropdown_y',
                                   labelStyle = {'cursor': 'pointer', 'margin-left':'20px'}),
                    dcc.Graph(id='main_pilot_plot')
                ], width=8),
                dbc.Col([
                    dcc.RadioItems(col_agg_instructor_df, 'Total_Duration', inline=True, id='instructor_dropdown_y',
                                   labelStyle = {'cursor': 'pointer', 'margin-left':'20px'}),
                    dcc.Graph(id='main_instructor_plot')
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H2('Aircrafts'),
                    html.Hr()
                ], width=12),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.RadioItems(col_agg_aircraft_df, 'Total_Flight_Time', inline=True, id='aircraft_dropdown_y',
                                   labelStyle = {'cursor': 'pointer', 'margin-left':'20px'})
                ], width=12)
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='aircraft_plot')
                ], width=4),
                dbc.Col([
                    dash_table.DataTable(id='aircraft_table',
        style_data={'backgroundColor': '#2e2e2e', 'color': 'white'},
        style_header={'backgroundColor': '#1f1f1f', 'fontWeight': 'bold'},
        style_cell={'textAlign': 'left'})
                ], width=8),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H2('Members'),
                    html.Hr()
                ], width=12),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='main_member_plot')
                ], width=4),
                dbc.Col([
                    dcc.Graph(id='member_join_plot')
                ], width=4),
                dbc.Col([
                    dcc.Graph(id='member_location_plot')
                ], width=4)
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H2('Reservation'),
                    html.Hr()
                ], width=12),
            ], align='center'),
            html.Br(),
                dbc.Row([
                dbc.Col([
                    dcc.RadioItems(col_agg_flight_res_df, 'Accepted_Reservation_Duration', inline=True, id='flight_res_radioitem',
                                   labelStyle = {'cursor': 'pointer', 'margin-left':'20px'})
                ], width=12)
            ], align='center'),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='main_reservation_plot')
                ], width=4),
                dbc.Col([
                    dcc.Graph(id='res_per_pilot_plot')
                ], width=8)
            ], align='center'),
        ]), color=layout_color
    )
])


# Callback for updating the graphs
@app.callback(
    [Output('main_flightlog_plot', 'figure'),
     Output('main_instructorlog_plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('dateformat_dropdown_x', 'value')]
)
def update_timeline_graphs(start_date, end_date, dateformat_dropdown_x_value):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    # Aggregate on Date
    grouped_flight_df = dp.date_aggregation(filtered_flight_df, dateformat_dropdown_x_value, 'Flight Time')
    # Create Main Flightlog Plot
    main_flightlog_plot = px.bar(
        grouped_flight_df,
        dateformat_dropdown_x_value,
        'Total_Time',
        color='Total_Time',
        template=plot_template,
        color_continuous_scale=color_scale
    )
    main_flightlog_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    main_flightlog_plot.update_layout(margin=plot_margin,
                                      paper_bgcolor=paper_bgcolor,
                                          plot_bgcolor=paper_bgcolor)

    # Filter Instructorlog data based on the selected date range
    filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)
    grouped_instructor_df = dp.date_aggregation(filtered_instructor_df,
                                                dateformat_dropdown_x_value,
                                                'Duration')
    # Create Main Instructorlog Plot
    main_instructorlog_plot = px.bar(
        grouped_instructor_df,
        dateformat_dropdown_x_value,
        'Total_Time',
        color='Total_Time',
        template=plot_template,
        color_continuous_scale=color_scale
    )

    main_instructorlog_plot.update_layout(margin=plot_margin,
                                          paper_bgcolor=paper_bgcolor,
                                          plot_bgcolor=paper_bgcolor)

    return main_flightlog_plot, main_instructorlog_plot


@app.callback(
    [Output('main_pilot_plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('pilot_dropdown_y', 'value')]
)
def update_pilot_graphs(start_date, end_date, pilot_dropdown_y_value):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df, pilot_dropdown_y_value)
    # Create Pilot Plot
    main_pilot_plot = px.bar(
        agg_pilot_df,
        'Pilot',
        pilot_dropdown_y_value,
        color=pilot_dropdown_y_value,
        template=plot_template,
        color_continuous_scale=color_scale
    )
    main_pilot_plot.update_layout(margin=plot_margin,
                                  paper_bgcolor=paper_bgcolor)

    return [main_pilot_plot]

@app.callback(
    [Output('main_instructor_plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('instructor_dropdown_y', 'value')]
)
def update_instructor_graph(start_date, end_date, instructor_dropdown_y):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter Instructorlog data based on the selected date range
    filtered_instructor_df = dp.date_select_df(instructor_df, start_date, end_date)
    # Aggregate Insturctor Data
    agg_instructor_df = dp.instructor_aggregation(filtered_instructor_df, instructor_dropdown_y)
    # Create Instructor Plot
    main_instructor_plot = px.bar(
        agg_instructor_df,
        'Instructor',
        instructor_dropdown_y,
        color=instructor_dropdown_y,
        template=plot_template,
        color_continuous_scale=color_scale
    )
    main_instructor_plot.update_layout(margin=plot_margin,
                                       paper_bgcolor=paper_bgcolor)

    return [main_instructor_plot]

@app.callback(
    [Output('aircraft_plot', 'figure'),
     Output('aircraft_table', 'data')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('aircraft_dropdown_y', 'value')]
)
def update_aircraft_graph(start_date, end_date, aircraft_dropdown_y):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # Filter Flightlog data based on the selected date range
    filtered_flight_df = dp.date_select_df(flight_df, start_date, end_date)
    # Aggregate Aircraft Data
    agg_aircraft_df = dp.aircraft_aggregation(filtered_flight_df)
    # Create AIrcraft Plot
    aircraft_plot = px.bar(
        agg_aircraft_df,
        "Aircraft",
        aircraft_dropdown_y,
        color="Total_Flight_Time",
        template=plot_template,
        color_continuous_scale=color_scale
    )
    aircraft_plot.update_layout(margin=plot_margin,
                                paper_bgcolor=paper_bgcolor)

    # Create Aircraft Table
    aircraft_table = agg_aircraft_df.to_dict('records')  # Convert DataFrame to list of dictionaries

    return [aircraft_plot, aircraft_table]

@app.callback(
    [Output('main_member_plot', 'figure'),
     Output('member_join_plot', 'figure'),
     Output('member_location_plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_member_graph(start_date, end_date):
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    agg_member_df = dp.member_aggregation(member_df)
    agg_member_df = agg_member_df[agg_member_df['Membership'] == 'Aktiv']

    main_member_plot = plots.member_histogram(member_df)

    member_join_plot = plots.memeber_join_linegraph(member_df)

    member_location_plot = plots.member_location_graph(member_df, gem_gdf)

    return main_member_plot, member_join_plot, member_location_plot

@app.callback(
    [Output('main_reservation_plot', 'figure'),
     Output('res_per_pilot_plot', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('flight_res_radioitem', 'value')]
)
def update_reservation_graph(start_date, end_date, flight_res_radioitem):
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


    # Create Reservation Plot
    main_reservation_plot = px.pie(
        reservation_sum,
        names=reservation_sum.index,
        values='count',
        template=plot_template,
        color_discrete_sequence=discrete_teal
    )
    main_reservation_plot.update_layout(margin=plot_margin,
                                paper_bgcolor=paper_bgcolor)

    agg_flight_res_df = dp.reservation_flight_merge(agg_reservation_df, agg_pilot_df, sort_column=flight_res_radioitem)

    res_per_pilot_plot = px.bar(
        agg_flight_res_df,
        'Pilot',
        flight_res_radioitem,
        color=flight_res_radioitem,
        template=plot_template,
        color_continuous_scale=color_scale
    )
    res_per_pilot_plot.update_layout(margin=plot_margin,
                                  paper_bgcolor=paper_bgcolor)


    return main_reservation_plot, res_per_pilot_plot

if __name__ == '__main__':
    # Run app
    app.run_server(debug=False)