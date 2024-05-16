# Pilot page

# Libraries
from icecream import ic  # Debugging library for printing variable values
import dash   # Core Dash library
from dash import Dash, dcc, html, callback, Input, Output, dash_table, State  # Dash components for building
import dash_bootstrap_components as dbc  # Dash components styled with Bootstrap
import pandas as pd  # Data manipulation library
import plotly.express as px  # Library for handling dates and times
import numpy as np
# Import other Files
import data_preparation as dp  # Custom module for data preparation tasks
import trend_calculation as tc
import string_func as sf
import globals  # Custom module for global variables and settings
import plot

globals.init()  # Initialize global variables

dash.register_page(__name__, path='/pilot', name='Pilot')  # Page Setup

layout = html.Div([
    # Dropdown Menu
    dbc.Row([
        dcc.Dropdown(value='⌀ All Pilots', id='Pilot-Dropdown')
    ]),
    # KPI Row Pilot
    dcc.Loading(
        id='loading-kpi-pilot',
        type='default',
        children=html.Div(
        dbc.Row([
            dbc.Col([
                dbc.Card([dbc.CardHeader("Pilot"),
                dbc.CardBody(
                [
                    html.H4("Name", id='Pilot-Name'),
                ]
            )
            ])
            ], **globals.adaptiv_width_3),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Flight Time"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Pilot-Flight-Hours'),
                    html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Flight-Hours-Trend')
                ]
            )
            ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Block Time"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Block-Hours'),
                              html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Block-Hours-Trend')
                          ]
                      )
                      ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Flt./Blckt."),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Flight-Block-Time'),
                              html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Flight-Block-Time-Trend')
                          ]
                      )
                      ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Flights"),
                dbc.CardBody(
                [
                    html.H4("XXX #", id='Pilot-Number-of-Flights'),
                    html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Number-of-Flights-Trend')
                ]
            )
            ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Landings"),
                dbc.CardBody(
                [
                    html.H4("XXX #", id='Pilot-Number-of-Landings'),
                    html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Number-of-Landings-Trend')
                ]
            )
            ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Flt/Res"),
                          dbc.CardBody(
                              [
                                  html.H4("XXX %", id='Pilot-Res-to-Flight-Time'),
                                  html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Res-to-Flight-Time-Trend')
                              ]
                          )
                          ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Reservations"),
                          dbc.CardBody(
                              [
                                  html.H4("XXX h", id='Pilot-Reservation'),
                                  html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Reservation-Trend')
                              ]
                          )
                          ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Cancelled"),
                          dbc.CardBody(
                              [
                                  html.H4("XXX h", id='Pilot-Cancelled'),
                                  html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Cancelled-Trend')
                              ]
                          )
                          ])
            ], **globals.adaptiv_width_1),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Canc. Ratio"),
                          dbc.CardBody(
                              [
                                  html.H4("XXX %", id='Pilot-Cancelled-Ratio'),
                                  html.H6("→ XX %", style={'color': 'grey'}, id='Pilot-Cancelled-Ratio-Trend')
                              ]
                          )
                          ])
            ], **globals.adaptiv_width_1)
        ], className="g-0"))),
    # First Row of Plots
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-Pilots-Flight-Time-Plot',
                                  type='cube',
                                  children=html.Div(
                                      dcc.Graph(id='Pilots-Flight-Time-Plot'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_8),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Cancellation Reason 🛈", id='Pilot-Cancel-Reason-Header'),
                      dbc.Tooltip('Based on the cancellation reason stated and compared against a keyword list',
                                          target='Pilot-Cancel-Reason-Header'),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-Pilot-Cancel-Reason',
                                  type='cube',
                                  children=html.Div(
                                      dcc.Graph(id='Pilot-Cancel-Reason'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_4)
    ], className="g-0"),
    # Datatable Pilots
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Pilots Logs", id='Pilots-Data-Table-Header'),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-Pilots-Data-Table',
                                  type='default',
                                  children=html.Div(
                                      html.Div(id="Pilots-Data-Table")))
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_12)
    ], className="g-0")
])

# Callback that populates the Dropdownmenu from the Data
@callback(Output('Pilot-Dropdown', 'options'),  # Dropdown Data
          Input('flightlog-store', 'data'),  # Flightlog Data Dict
          Input('date-picker-range', 'start_date'),
          Input('date-picker-range', 'end_date'))
def update_dropdown(flightlog_dict, start_date, end_date):
    if flightlog_dict is None: # If no Flightlog Data is Available
        pilots = []
        pilots = np.append(pilots, '⌀ All Pilots') # Append the generic Item to list
        return pilots

    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    pilots = filtered_flight_df['Pilot'].sort_values().unique()  # Get Unique Pilots
    # Append '⌀ All Pilots' to the array of unique pilot names
    pilots = np.append(pilots, '⌀ All Pilots')

    return pilots

@callback(
    [Output('Pilot-Name', 'children')],  # Name of Pilot
    [Input('Pilot-Dropdown', 'value')]  # Selected Pilot from Dropdown
)
def update_pilots_name(pilot_dropdown):
    return [pilot_dropdown]

# Callback that handles the KPI form the Flightlog per Pilot
@callback(
    [Output('Pilot-Flight-Hours', 'children'),  # KPI Flight hours
     Output('Pilot-Flight-Hours-Trend', 'children'),  # KPI Flight hours Trend
     Output('Pilot-Flight-Hours-Trend', 'style'),  # KPI Flight hours Trend Style

     Output('Pilot-Block-Hours', 'children'),  # KPI Block Hours
     Output('Pilot-Block-Hours-Trend', 'children'),  # KPI Block Hours Trend
     Output('Pilot-Block-Hours-Trend', 'style'),  # KPI Block Hours Trend Style

     Output('Pilot-Flight-Block-Time', 'children'),  # KPI Ratio Flight to Block
     Output('Pilot-Flight-Block-Time-Trend', 'children'),  # KPI Ratio Flight to Block Trend
     Output('Pilot-Flight-Block-Time-Trend', 'style'),  # KPI Ratio Flight to Block

     Output('Pilot-Number-of-Flights', 'children'),  # KPI Number of Flights
     Output('Pilot-Number-of-Flights-Trend', 'children'),  # KPI Number of Flights Trend
     Output('Pilot-Number-of-Flights-Trend', 'style'),  # KPI Number of Flights Trend Style

     Output('Pilot-Number-of-Landings', 'children'),  # KPI Number of Landings
     Output('Pilot-Number-of-Landings-Trend', 'children'),  # KPI Number of Landings Trend
     Output('Pilot-Number-of-Landings-Trend', 'style')],  # KPI Number of Landings Trend Style

    [Input('flightlog-store', 'data'),  # Flight log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Datepicker
     Input('date-picker-range', 'end_date'),  # End Date form Datepicker
     Input('Pilot-Dropdown', 'value')]  # Selected Pilot from Dropdown
)
def update_pilots_header_flightpart(flightlog_dict, start_date, end_date, pilot_dropdown):
    if flightlog_dict is None: # If no Flightlog is available
        sum_flight_time, sum_block_time, flight_block_ratio, \
            sum_flights, sum_landings = ('NO DATA',) * 5
        sum_flight_time_trend, sum_block_time_trend, flight_block_ratio_trend, \
            sum_flights_trend, sum_landings_trend = ('trend n/a',) * 5
        sum_flight_time_trend_style, sum_block_time_trend_style, flight_block_ratio_trend_style, \
            sum_flights_trend_style, sum_landings_trend_style = ({'color': 'grey'},) * 5
        return [sum_flight_time, sum_flight_time_trend, sum_flight_time_trend_style,
                sum_block_time, sum_block_time_trend, sum_block_time_trend_style,
                flight_block_ratio, flight_block_ratio_trend, flight_block_ratio_trend_style,
                sum_flights, sum_flights_trend, sum_flights_trend_style,
                sum_landings, sum_landings_trend, sum_landings_trend_style]

    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)
    try:  # Try reload of with offset of one year
        # Check if the time difference is over one year
        if abs((pd.Timestamp(start_date) - pd.Timestamp(end_date)).days) > 365:
            raise ValueError("Difference is over a Year.")
        # Reload with offset
        offset = 1  # in years
        filtered_flight_df_trend = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date,
                                                                           offset)
        # Aggregate Pilots Data
        agg_pilot_df_trend = dp.pilot_aggregation(filtered_flight_df_trend)
        if len(filtered_flight_df_trend) < 1:
            raise ValueError("Empty Dataframe")
        # Select kpi and select kpi minus offset
        selected, selected_t_minus = tc.select_pilot_page_flightlog(agg_pilot_df,
                                                                       agg_pilot_df_trend,
                                                                       pilot_dropdown)
        kpi = sf.trend_string_pilot_page_flightlog(selected)
        # Get Return list with trend
        trend_strings, trend_styles = tc.trend_calculation(selected, selected_t_minus)
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    except Exception as e:  # If over one year or not possible to load Data
        print(e)
        selected = tc.sum_pilot_page_flightlog(agg_pilot_df, pilot_dropdown)  # Only the Kpis
        kpi = sf.trend_string_pilot_page_flightlog(selected)
        trend_strings, trend_styles = sf.trend_string(len(selected))
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    return return_list

# Callback that handles Reservationslog KPIs
@callback(
    [
     Output('Pilot-Reservation', 'children'),  # KPI Pilots Reservations
     Output('Pilot-Reservation-Trend', 'children'),  # KPI Pilots Reservations Trend
     Output('Pilot-Reservation-Trend', 'style'),  # KPI Pilots Reservations Trend Style

     Output('Pilot-Cancelled', 'children'),  # KPI Reservation cancelled
     Output('Pilot-Cancelled-Trend', 'children'),  # KPI Reservation cancelled Trend
     Output('Pilot-Cancelled-Trend', 'style')],  # KPI Reservation cancelled Trend Style

    [Input('reservationlog-store', 'data'),  # Reservation log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Date Picker
     Input('date-picker-range', 'end_date'),  # End Date from Date Picker
     Input('Pilot-Dropdown', 'value')],  # Value from Dropdown
)
def update_pilots_header_reservationpart(reservationlog_dict, start_date, end_date, pilot_dropdown):
    if reservationlog_dict is None:  # If No Reservations log Data is available
        reservations, cancelled = ('NO DATA',) * 2
        reservations_trend, cancelled_trend = ('trend n/a',) * 2
        reservations_trend_style, cancelled_trend_style = ({'color': 'grey'},) * 2
        return [reservations, reservations_trend, reservations_trend_style,
                cancelled, cancelled_trend, cancelled_trend_style]

    # reload dataframe form dict
    filtered_flight_df = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date)
    # Aggregate Pilots Data
    agg_reservation_df = dp.reservation_aggregation(filtered_flight_df)
    try:  # Try reload of with offset of one year
        # Check if the time difference is over one year
        if abs((pd.Timestamp(start_date) - pd.Timestamp(end_date)).days) > 365:
            raise ValueError("Difference is over a Year.")
        # Reload with offset
        offset = 1  # in years
        filtered_reservation_df_trend = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date,
                                                                           offset)
        # Aggregate Pilots Data
        agg_reservation_df_trend = dp.reservation_aggregation(filtered_reservation_df_trend)
        if len(filtered_reservation_df_trend) < 1:
            raise ValueError("Empty Dataframe")
        # Select kpi and select kpi minus offset
        selected, selected_t_minus = tc.select_pilot_page_reservationlog(agg_reservation_df,
                                                                       agg_reservation_df_trend,
                                                                       pilot_dropdown)
        kpi = sf.trend_string_pilot_page_reservationlog(selected)
        # Get Return list with trend
        trend_strings, trend_styles = tc.trend_calculation(selected, selected_t_minus)
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    except Exception as e:  # If over one year or not possible to load Data
        print(e)
        selected = tc.sum_pilot_page_reservationlog(agg_reservation_df, pilot_dropdown)  # Only the Kpis
        kpi = sf.trend_string_pilot_page_reservationlog(selected)
        trend_strings, trend_styles = sf.trend_string(len(selected))
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    return return_list

# Callback that handles the combined KPIs from Flightlog and Reservation log
@callback(
    [
     Output('Pilot-Res-to-Flight-Time', 'children'),  # KPI Flight to Res Time
     Output('Pilot-Res-to-Flight-Time-Trend', 'children'),  # KPI Flight to Res Time Trend
     Output('Pilot-Res-to-Flight-Time-Trend', 'style'),  # KPI Flight to Res Time Trend Style

     Output('Pilot-Cancelled-Ratio', 'children'),  # KPI Cancelled Ratio
     Output('Pilot-Cancelled-Ratio-Trend', 'children'),  # KPI Cancelled Ratio Trend
     Output('Pilot-Cancelled-Ratio-Trend', 'style')],  # KPI Cancelled Ratio Trend Style

    [Input('flightlog-store', 'data'),  # Flight log Data Dict
     Input('reservationlog-store', 'data'),  # Reservation Log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Date Picker
     Input('date-picker-range', 'end_date'),  # End Date from Date Picker
     Input('Pilot-Dropdown', 'value')]  # Selected Pilot from Dropdown
)
def update_pilots_header_combined_part(flightlog_dict, reservationlog_dict, start_date, end_date, pilot_dropdown):
    if flightlog_dict is None or reservationlog_dict is None:  # If one of the logs is not available
        res_flight_time, cancelled_ratio = ('NO DATA',) * 2
        res_flight_time_trend, cancelled_ratio_trend = ('trend n/a',) * 2
        res_flight_time_trend_style, cancelled_ratio_trend_style = ({'color': 'grey'},) * 2
        return [res_flight_time, res_flight_time_trend, res_flight_time_trend_style,
                cancelled_ratio, cancelled_ratio_trend, cancelled_ratio_trend_style]



    # reload flightlog dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    # reload reservation dataframe form dict
    filtered_reservation_df = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date)

    agg_reservation_df = dp.reservation_aggregation(filtered_reservation_df)  # aggregate reservations log
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df) # Aggregate Flight log Data
    agg_flight_res_df = dp.reservation_flight_merge(agg_reservation_df, agg_pilot_df) # Merge the flight and reservation log

    try:  # Try reload of with offset of one year
        # Check if the time difference is over one year
        if abs((pd.Timestamp(start_date) - pd.Timestamp(end_date)).days) > 365:
            raise ValueError("Difference is over a Year.")
        # Reload with offset
        offset = 1  # in years

        filtered_flight_df_trend = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date,
                                                                           offset)
        filtered_reservation_df_trend = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date,
                                                                           offset)

        agg_reservation_df_trend = dp.reservation_aggregation(filtered_reservation_df_trend)  # aggregate reservations log
        agg_pilot_df_trend = dp.pilot_aggregation(filtered_flight_df_trend)  # Aggregate Flight log Data
        agg_flight_res_df_trend = dp.reservation_flight_merge(agg_reservation_df_trend,
                                                        agg_pilot_df_trend)  # Merge the flight and reservation log


        if len(filtered_flight_df_trend) < 1:
            raise ValueError("Empty Dataframe")
        # Select kpi and select kpi minus offset
        selected, selected_t_minus = tc.select_pilot_page_flight_reservation_log(agg_flight_res_df,
                                                                       agg_flight_res_df_trend,
                                                                       pilot_dropdown)
        kpi = sf.trend_string_pilot_page_flight_reservation_log(selected)
        # Get Return list with trend
        trend_strings, trend_styles = tc.trend_calculation(selected, selected_t_minus)
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    except Exception as e:  # If over one year or not possible to load Data
        print(e)
        selected = tc.sum_pilot_page_flight_reservation_log(agg_flight_res_df, pilot_dropdown)  # Only the Kpis
        kpi = sf.trend_string_pilot_page_flight_reservation_log(selected)
        trend_strings, trend_styles = sf.trend_string(len(selected))
        return_list = [item for sublist in zip(kpi, trend_strings, trend_styles) for item in sublist]

    return return_list


# Callback that handles the Flight Time Graph
@callback(
    [Output('Pilots-Flight-Time-Plot', 'figure')],  # Flight Time Graph
    [Input('flightlog-store', 'data'),  # Flight log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Date Picker
     Input('date-picker-range', 'end_date'),  # End Date from Date Picker
     Input('Pilot-Dropdown', 'value')]  # Value from Pilots Dropdown
)
def update_pilot_graphs(flightlog_dict, start_date, end_date, pilot_dropdown):
    if flightlog_dict is None:  # If no Flight log Data is available
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)
    # Create Pilot Plot
    pilots_flight_time_plot = px.bar(
        agg_pilot_df,
        'Pilot',
        'Total_Flight_Time',
        color='Total_Flight_Time',
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale
    )
    # Update the color of the bar Plot so the Pilot selected is visable
    if pilot_dropdown != '⌀ All Pilots':
        pilots_flight_time_plot.update_traces(
            marker=dict(color=[globals.discrete_teal[-1] if pilot == pilot_dropdown else globals.discrete_teal[0] for pilot in agg_pilot_df['Pilot']]),
            hovertext=agg_pilot_df['Total_Flight_Time'],
            selector=dict(type='bar')
        )
    pilots_flight_time_plot.update(layout_coloraxis_showscale=False)
    pilots_flight_time_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    pilots_flight_time_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)

    # Calculate the mean of Total_Flight_Time
    mean_flight_time = agg_pilot_df['Total_Flight_Time'].mean()

    # Add a horizontal line for the mean
    pilots_flight_time_plot.add_hline(y=mean_flight_time, line_dash="dash", line_color='rgba(0,203,233,255)', line_width=4)

    return [pilots_flight_time_plot]


# Callback that handles the Reservations Log Graph
@callback(
    [Output('Pilot-Cancel-Reason', 'figure')],  # Reservations log Graph
    [Input('reservationlog-store', 'data'),  # Reservations log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Date Picker
     Input('date-picker-range', 'end_date'),  # End Date from Date Picker
     Input('Pilot-Dropdown', 'value')]  # Selected Pilot in Dropdown
)
def update_reservation_graph(reservationlog_dict, start_date, end_date, pilot_dropdown):
    if reservationlog_dict is None:  # If no Reservationslog is Available
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_reservation_df = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date)
    if pilot_dropdown != '⌀ All Pilots':  # If All Pilts are Selected
        filtered_reservation_df = filtered_reservation_df[filtered_reservation_df['Pilot']==pilot_dropdown]
    reservation_sum = filtered_reservation_df[filtered_reservation_df['Deleted']]['Deletion Reason'].value_counts()

    # Create Reservation Plot
    pilot_cancel_reason_plot = px.pie(
        reservation_sum,
        names=reservation_sum.index,
        values='count',
        template=globals.plot_template,
        color_discrete_sequence=globals.discrete_teal
    )
    pilot_cancel_reason_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    pilot_cancel_reason_plot.update_layout(margin=globals.plot_margin,
                                       paper_bgcolor=globals.paper_bgcolor,
                                       plot_bgcolor=globals.paper_bgcolor,
                                       legend=globals.legend)

    return [pilot_cancel_reason_plot]

# Callback that handles the Datatable for Pilots
@callback(
    [Output('Pilots-Data-Table', 'children'),  # Datatable
     Output('Pilots-Data-Table-Header', 'children'),],  # CardHeader with Name of Pilots
    [State('flightlog-store', 'data'),  # Flight log Data Dict
     Input('date-picker-range', 'start_date'),  # Start Date from Date Picker
     Input('date-picker-range', 'end_date'),  # End Date from Date Picker
     Input('Pilot-Dropdown', 'value')]  # Selected Pilot form Dropdown
)
def update_pilots_header_flightpart(flightlog_dict, start_date, end_date, pilot_dropdown):
    if flightlog_dict is None:  # If no Flight Log Data is available
        df = pd.DataFrame()
        return [dash_table.DataTable(df.to_dict('records')), 'Pilots Log [No Data]']
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    if pilot_dropdown != '⌀ All Pilots':  # If all Pilots are Selected
        filtered_flight_df = filtered_flight_df[filtered_flight_df['Pilot']==pilot_dropdown]

    filtered_flight_df = filtered_flight_df[['Date', 'Pilot', 'Flight Type', 'Flight Time', 'Block Time', 'Landings',
                                             'Aircraft', 'Departure Location', 'Arrival Location']]
    # Formatieren der 'timestamp'-Spalte in 'HH:MM'
    filtered_flight_df['Flight Time'] = round(filtered_flight_df['Flight Time'].dt.total_seconds() / 3600, 2)
    filtered_flight_df['Block Time'] = round(filtered_flight_df['Block Time'].dt.total_seconds() / 3600, 2)

    dict = filtered_flight_df.to_dict('records')  # Change to Dict for Dash Data Table

    table = dash_table.DataTable(data=dict,
                                 columns=[  # Setup for Columns
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
                                 page_size=16,  # Listed Entrys per Page
                                 filter_action="native",
                                 sort_action='native',
                                 tooltip_data=[
                                     {  # Tool Tip so overflow can be visable in a Popup
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

    header = f'Pilots Log {pilot_dropdown}'


    return [table, header]