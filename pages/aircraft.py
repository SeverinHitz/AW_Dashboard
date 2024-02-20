# Aircraft page

# Libraries
from icecream import ic
import dash
from dash import Dash, dcc, html, callback, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
# Import other Files
import data_preparation as dp
import globals
import plot

globals.init()


eu_airports_file = 'eu-airports.csv'

eu_airport_gdf = dp.load_eu_airports(eu_airports_file)



dash.register_page(__name__, path='/aircraft', name='Aircraft')


layout = html.Div([
    dbc.Row([
        dcc.Dropdown(value='⌀ All Aircrafts', id='Aircraft-Dropdown')
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Aircraft"),
            dbc.CardBody(
            [
                html.H4("Name", id='Aircraft-Registration'),
            ]
        )
        ])
        ], **globals.adaptiv_width_3),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Aircraft-Flight-Hours'),
            ]
        )
        ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flights"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Aircraft-Number-of-Flights'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("⌀ Flt Time"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Aircraft-Mean-Flight-Time'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Landings"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Aircraft-Number-of-Landings'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Airports"),
                      dbc.CardBody(
                          [
                              html.H4("XXX #", id='Aircraft-Number-of-Airports'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Fuel p. h."),
            dbc.CardBody(
            [
                html.H4("XXX L", id='Aircraft-Fuel-per-Hour'),
            ]
        )
        ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Oil p. h."),
            dbc.CardBody(
            [
                html.H4("XXX mL", id='Aircraft-Oil-per-Hour'),
            ]
        )
        ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Inst. Ratio"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Aircraft-Instruction-Ratio'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_1),
        dbc.Col([
            dbc.Card([dbc.CardHeader("# Pilots"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Aircraft-Number-of-Pilots'),
            ]
        )
        ])
        ], **globals.adaptiv_width_1),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Aircraft-Flight-Time-Plot'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_4),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Type"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Aircraft-Flight-Type-Plot'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_4),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Heatmap"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Aircraft-Heatmap'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_4)
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Aircraft Logs", id='Aircraft-Data-Table-Header'),
                      dbc.CardBody(
                          [
                          html.Div(id="Aircraft-Data-Table")
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_12)
    ], className="g-0")
])

@callback(Output('Aircraft-Dropdown', 'options'),
          Input('flightlog-store', 'data'),
          Input('date-picker-range', 'start_date'),
          Input('date-picker-range', 'end_date'))
def update_dropdown(flightlog_dict, start_date, end_date):
    if flightlog_dict is None:
        aircrafts = []
        aircrafts = np.append(aircrafts, '⌀ All Aircrafts')
        return aircrafts
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    aircrafts = filtered_flight_df['Aircraft'].sort_values().unique()
    # Append '⌀ All Pilots' to the array of unique pilot names
    aircrafts = np.append(aircrafts, '⌀ All Aircrafts')

    return aircrafts




@callback(
    [Output('Aircraft-Registration', 'children'),
     Output('Aircraft-Flight-Hours', 'children'),
     Output('Aircraft-Number-of-Flights', 'children'),
     Output('Aircraft-Mean-Flight-Time', 'children'),
     Output('Aircraft-Number-of-Landings', 'children'),
     Output('Aircraft-Number-of-Airports', 'children'),
     Output('Aircraft-Fuel-per-Hour', 'children'),
     Output('Aircraft-Oil-per-Hour', 'children'),
     Output('Aircraft-Instruction-Ratio', 'children'),
     Output('Aircraft-Number-of-Pilots', 'children')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Aircraft-Dropdown', 'value')]
)
def update_pilots_header(flightlog_dict, start_date, end_date, aircraft_dropdown):
    if flightlog_dict is None:
        aircraft_dropdown, sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots = ('NO DATA',) * 10
        return aircraft_dropdown, sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    # Aggregate Pilots Data
    agg_aircraft_df = dp.aircraft_aggregation(filtered_flight_df)

    if aircraft_dropdown == '⌀ All Aircrafts':
        agg_aircraft_df = agg_aircraft_df.iloc[:, 1:].mean().to_frame().T
    else:
        agg_aircraft_df = agg_aircraft_df[agg_aircraft_df['Aircraft']==aircraft_dropdown]

    if len(agg_aircraft_df)==1:
        # Aircraft-Flight-Hours
        sum_flight_time = f'{agg_aircraft_df.iloc[0]["Total_Flight_Time"]:.1f} h'
        # Aircraft-Number-of-Flights
        sum_flights = f'{agg_aircraft_df.iloc[0]["Number_of_Flights"]:.0f} #'
        # Aircraft-Mean-Flight-Time
        mean_flight_time = f'{agg_aircraft_df.iloc[0]["Mean_Flight_Time"]*60:.0f} min'
        # Aircraft-Number-of-Landings
        sum_landings = f'{agg_aircraft_df.iloc[0]["Number_of_Landings"]:.0f} #'
        # Aircraft-Number-of-Airports
        sum_airports = f'{agg_aircraft_df.iloc[0]["Number_of_Different_Airports"]:.0f} #'
        # Aircraft-Fuel-per-Hour
        fuel_per_hour = f'{agg_aircraft_df.iloc[0]["Fuel_per_hour"]:.1f} L'
        # Aircraft-Oil-per-Hour
        oil_per_hour = f'{agg_aircraft_df.iloc[0]["Oil_per_hour"]*1000:.0f} mL'
        # Aircraft-Instruction-Ratio
        instruction_ratio = f'{agg_aircraft_df.iloc[0]["Instruction_Ratio"]*100:.1f} %'
        # Aircraft-Number-of-Pilots
        sum_pilots = f'{agg_aircraft_df.iloc[0]["Number_of_Pilots"]:.0f} #'
    else:
        aircraft_dropdown, sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots = ('NO DATA',) * 10

    return aircraft_dropdown, sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots


@callback(
    [Output('Aircraft-Flight-Time-Plot', 'figure')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Aircraft-Dropdown', 'value')]
)
def update_aircraft_flight_time_plot(flightlog_dict, start_date, end_date, aircraft_dropdown):
    if flightlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    # Aggregate Pilots Data
    agg_aircraft_df = dp.aircraft_aggregation(filtered_flight_df)
    # Create Pilot Plot
    aircraft_flight_time_plot = px.bar(
        agg_aircraft_df,
        'Aircraft',
        'Total_Flight_Time',
        color='Total_Flight_Time',
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale
    )
    # Update the color of the selected pilot in the bar plot
    if aircraft_dropdown != '⌀ All Aircrafts':
        aircraft_flight_time_plot.update_traces(
            marker=dict(color=[globals.discrete_teal[-1] if aircraft == aircraft_dropdown else globals.discrete_teal[0]\
                               for aircraft in agg_aircraft_df['Aircraft']]),
            hovertext=agg_aircraft_df['Total_Flight_Time'],
            selector=dict(type='bar')
        )
    aircraft_flight_time_plot.update(layout_coloraxis_showscale=False)
    aircraft_flight_time_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    aircraft_flight_time_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)

    return [aircraft_flight_time_plot]


@callback(
    [Output('Aircraft-Flight-Type-Plot', 'figure')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Aircraft-Dropdown', 'value')]
)
def update_aircraft_flight_type_plot(flightlog_dict, start_date, end_date, aircraft_dropdown):
    if flightlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    if aircraft_dropdown != '⌀ All Aircrafts':
        filtered_flight_df = filtered_flight_df[filtered_flight_df['Aircraft']==aircraft_dropdown]
    flight_type_sum = filtered_flight_df['Flight Type'].value_counts()

    # Create Reservation Plot
    aircraft_flight_type_plot = px.pie(
        flight_type_sum,
        names=flight_type_sum.index,
        values='count',
        template=globals.plot_template,
        color_discrete_sequence=globals.discrete_teal
    )
    aircraft_flight_type_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    aircraft_flight_type_plot.update_layout(margin=globals.plot_margin,
                                       paper_bgcolor=globals.paper_bgcolor,
                                       plot_bgcolor=globals.paper_bgcolor,
                                       legend=globals.legend)

    return [aircraft_flight_type_plot]

@callback(
    [Output('Aircraft-Heatmap', 'figure')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Aircraft-Dropdown', 'value')]
)
def update_aircraft_heat_map(flightlog_dict, start_date, end_date, aircraft_dropdown):
    if flightlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    if aircraft_dropdown != '⌀ All Aircrafts':
        filtered_flight_df = filtered_flight_df[filtered_flight_df['Aircraft']==aircraft_dropdown]
    arrival_count = dp.destination_aggregation(filtered_flight_df, eu_airport_gdf)

    # Get Center of Most Flown Airport:
    max_landing_row = arrival_count.loc[arrival_count['Total_Landings'].idxmax()]
    # Extract the latitude and longitude values from the row
    max_latitude = max_landing_row['latitude_deg']
    max_longitude = max_landing_row['longitude_deg']


    # Create Reservation Plot
    aircraft_heatmap = px.density_mapbox(
        arrival_count,
        lat='latitude_deg',
        lon='longitude_deg',
        z='log_Total_Landings',
        hover_name='ident',
        hover_data='Total_Landings',
        center={"lat": max_latitude, "lon": max_longitude},
        zoom=6,
        radius=50,
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale,
        mapbox_style="carto-darkmatter"
    )
    aircraft_heatmap.update(layout_coloraxis_showscale=False)
    aircraft_heatmap.update_layout(margin=globals.plot_margin_map,
                                            paper_bgcolor=globals.paper_bgcolor,
                                            plot_bgcolor=globals.paper_bgcolor,
                                            legend=globals.legend)

    return [aircraft_heatmap]


@callback(
    [Output('Aircraft-Data-Table', 'children'),
     Output('Aircraft-Data-Table-Header', 'children'),],
    [State('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Aircraft-Dropdown', 'value')]
)
def update_aircrafts_header_flightpart(flightlog_dict, start_date, end_date, aircraft_dropdown):
    if flightlog_dict is None:
        df = pd.DataFrame()
        return [dash_table.DataTable(df.to_dict('records')), 'Aircrafts Log [No Data]']
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    if aircraft_dropdown != '⌀ All Aircrafts':
        filtered_flight_df = filtered_flight_df[filtered_flight_df['Aircraft']==aircraft_dropdown]

    filtered_flight_df = filtered_flight_df[['Date', 'Aircraft', 'Pilot', 'Flight Type', 'Flight Time', 'Block Time',
                                             'Landings', 'Departure Location', 'Arrival Location']]
    # Formatieren der 'timestamp'-Spalte in 'HH:MM'
    filtered_flight_df['Flight Time'] = round(filtered_flight_df['Flight Time'].dt.total_seconds() / 3600, 2)
    filtered_flight_df['Block Time'] = round(filtered_flight_df['Block Time'].dt.total_seconds() / 3600, 2)

    dict = filtered_flight_df.to_dict('records')

    table = dash_table.DataTable(data=dict,
                                 columns=[
                                     {"name": i, "id": i, "deletable": True, "selectable": True} for i in filtered_flight_df.columns
                                 ],
                                 style_header={
                                     'backgroundColor': 'rgb(30, 30, 30)',
                                     'color': 'white'
                                 },
                                 style_data={
                                     'backgroundColor': 'rgb(50, 50, 50)',
                                     'color': 'white'
                                 },
                                 page_size=16,
                                 filter_action="native",
                                 sort_action='native',
                                 tooltip_data=[
                                     {
                                         column: {'value': str(value), 'type': 'markdown'}
                                         for column, value in row.items()
                                     } for row in filtered_flight_df.to_dict('records')
                                 ],

                                 # Overflow into ellipsis
                                 style_cell={
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis',
                                     'maxWidth': 0,
                                 },
                                 tooltip_delay=0,
                                 export_format='xlsx',
                                 export_headers='display',
                                 )

    header = f'Aircrafts Log {aircraft_dropdown}'


    return [table, header]