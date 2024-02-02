# Pilot page

# Libraries
from icecream import ic
import dash
from dash import Dash, dcc, html, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import numpy as np
# Import other Files
import data_preparation as dp
import globals
import plot

globals.init()



dash.register_page(__name__, path='/pilot', name='Pilot')

layout = html.Div([
    dbc.Row([
        dcc.Dropdown(value='⌀ All Pilots', id='Pilot-Dropdown')
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Pilot"),
            dbc.CardBody(
            [
                html.H4("Name", id='Pilot-Name'),
            ]
        )
        ])
        ], md=globals.adaptiv_width_3['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
            dbc.CardBody(
            [
                html.H4("XXX h", id='Pilot-Flight-Hours'),
            ]
        )
        ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Block Time"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Block-Hours'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flt./Blckt."),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Flight-Block-Time'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flights"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Pilot-Number-of-Flights'),
            ]
        )
        ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Landings"),
            dbc.CardBody(
            [
                html.H4("XXX #", id='Pilot-Number-of-Landings'),
            ]
        )
        ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flt/Res"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Res-to-Flight-Time'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Reservations"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Pilot-Reservation'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Cancelled"),
                      dbc.CardBody(
                          [
                              html.H4("XXX h", id='Pilot-Cancelled'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_1['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Canc. Ratio"),
                      dbc.CardBody(
                          [
                              html.H4("XXX %", id='Pilot-Cancelled-Ratio'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_1['md'])
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flight Time"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Pilots-Flight-Time-Plot'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_8['md']),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Cancellation Reason"),
                      dbc.CardBody(
                          [
                              dcc.Graph(id='Pilot-Cancel-Reason'),
                          ]
                      )
                      ])
        ], md=globals.adaptiv_width_4['md'])
    ], className="g-0")
])

@callback(Output('Pilot-Dropdown', 'options'),
          Input('flightlog-store', 'data'),
          Input('date-picker-range', 'start_date'),
          Input('date-picker-range', 'end_date'))
def update_dropdown(flightlog_dict, start_date, end_date):
    if flightlog_dict is None:
        pilots = []
        pilots = np.append(pilots, '⌀ All Pilots')
        return pilots

    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    pilots = filtered_flight_df['Pilot'].sort_values().unique()
    # Append '⌀ All Pilots' to the array of unique pilot names
    pilots = np.append(pilots, '⌀ All Pilots')

    return pilots

@callback(
    [Output('Pilot-Name', 'children'),
     Output('Pilot-Flight-Hours', 'children'),
     Output('Pilot-Block-Hours', 'children'),
     Output('Pilot-Flight-Block-Time', 'children'),
     Output('Pilot-Number-of-Flights', 'children'),
     Output('Pilot-Number-of-Landings', 'children')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_pilots_header_flightpart(flightlog_dict, start_date, end_date, pilot_dropdown):
    if flightlog_dict is None:
        pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio, \
            sum_flights, sum_landings = ('NO DATA',) * 6
        return pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio,\
            sum_flights, sum_landings
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)

    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)

    if pilot_dropdown == '⌀ All Pilots':
        agg_pilot_df = agg_pilot_df.iloc[:, 1:].mean().to_frame().T
    else:
        agg_pilot_df = agg_pilot_df[agg_pilot_df['Pilot']==pilot_dropdown]

    if len(agg_pilot_df)==1:
        # Pilots Flight Time
        sum_flight_time = f'{agg_pilot_df.iloc[0]["Total_Flight_Time"]:.1f} h'
        # Pilots Number of Flights
        sum_block_time = f'{agg_pilot_df.iloc[0]["Total_Block_Time"]:.1f} h'
        # Pilots Flight to Block Time
        flight_block_ratio = f'{agg_pilot_df.iloc[0]["Flight_Block_Ratio"]*100:.2f} %'
        # Pilots Number of Flights
        sum_flights = f'{agg_pilot_df.iloc[0]["Number_of_Flights"]:.0f} #'
        # Pilots Landings
        sum_landings = f'{agg_pilot_df.iloc[0]["Number_of_Landings"]:.0f} #'
    else:
        pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio, \
            sum_flights, sum_landings = ('NO DATA',) * 6

    return pilot_dropdown, sum_flight_time, sum_block_time, flight_block_ratio,\
        sum_flights, sum_landings

@callback(
    [
     Output('Pilot-Reservation', 'children'),
     Output('Pilot-Cancelled', 'children')],
    [Input('reservationlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_pilots_header(reservationlog_dict, start_date, end_date, pilot_dropdown):
    if reservationlog_dict is None:
        reservations, cancelled = ('NO DATA',) * 2
        return reservations, cancelled
    # reload dataframe form dict
    filtered_reservation_df = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date)

    agg_reservation_df = dp.reservation_aggregation(filtered_reservation_df)
    if pilot_dropdown == '⌀ All Pilots':
        agg_reservation_df = agg_reservation_df.iloc[:, 1:].mean().to_frame().T
    else:
        agg_reservation_df = agg_reservation_df[agg_reservation_df['Pilot']==pilot_dropdown]

    if len(agg_reservation_df)==1:
        # Pilots Cancelled Reservation
        reservations = f'{agg_reservation_df.iloc[0]["Reservations"]:.0f} #'
        # Pilots Cancelled Reservation
        cancelled = f'{agg_reservation_df.iloc[0]["Cancelled"]:.0f} #'
    else:
        reservations, cancelled = ('NO DATA',) * 2

    return reservations, cancelled

@callback(
    [
     Output('Pilot-Res-to-Flight-Time', 'children'),
     Output('Pilot-Cancelled-Ratio', 'children')],
    [Input('flightlog-store', 'data'),
     Input('reservationlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_pilots_header(flightlog_dict, reservationlog_dict, start_date, end_date, pilot_dropdown):
    if flightlog_dict is None or reservationlog_dict is None:
        res_flight_time, cancelled_ratio = ('NO DATA',) * 2
        return res_flight_time, cancelled_ratio
    # reload dataframe form dict
    filtered_flight_df = dp.reload_flightlog_dataframe_from_dict(flightlog_dict, start_date, end_date)
    # reload dataframe form dict
    filtered_reservation_df = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date)

    reservation_sum = filtered_reservation_df[filtered_reservation_df['Deleted']]['Deletion Reason'].value_counts()
    agg_reservation_df = dp.reservation_aggregation(filtered_reservation_df)

    # Aggregate Pilots Data
    agg_pilot_df = dp.pilot_aggregation(filtered_flight_df)

    agg_flight_res_df = dp.reservation_flight_merge(agg_reservation_df, agg_pilot_df)
    if pilot_dropdown == '⌀ All Pilots':
        agg_flight_res_df = agg_flight_res_df.iloc[:, 1:].mean().to_frame().T
    else:
        agg_flight_res_df = agg_flight_res_df[agg_flight_res_df['Pilot']==pilot_dropdown]

    if len(agg_flight_res_df)==1:
        # Pilots Reservations to Flighttime
        res_flight_time = f'{agg_flight_res_df.iloc[0]["Flight_to_Reservation_Time"]*100:.2f} %'
        # Pilots Cancelled Ratio
        cancelled_ratio = f'{agg_flight_res_df.iloc[0]["Ratio_Cancelled"]*100:.2f} %'
    else:
        res_flight_time, cancelled_ratio = ('NO DATA',) * 2

    return res_flight_time, cancelled_ratio


@callback(
    [Output('Pilots-Flight-Time-Plot', 'figure')],
    [Input('flightlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_pilot_graphs(flightlog_dict, start_date, end_date, pilot_dropdown):
    if flightlog_dict is None:
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
    # Update the color of the selected pilot in the bar plot
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

    return [pilots_flight_time_plot]

@callback(
    [Output('Pilot-Cancel-Reason', 'figure')],
    [Input('reservationlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Pilot-Dropdown', 'value')]
)
def update_reservation_graph(reservationlog_dict, start_date, end_date, pilot_dropdown):
    if reservationlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_reservation_df = dp.reload_reservation_dataframe_from_dict(reservationlog_dict, start_date, end_date)
    if pilot_dropdown != '⌀ All Pilots':
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

