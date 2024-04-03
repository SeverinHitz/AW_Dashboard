# School page

# Libraries
from icecream import ic
import dash
from dash import Dash, dcc, html, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
# Import other Files
import data_preparation as dp
import globals
import plot

globals.init()

dash.register_page(__name__, path='/school', name='School')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(value='Σ All Trainees', id='Trainee-Dropdown')
        ], **globals.adaptiv_width_6),
        dbc.Col([
            dcc.Dropdown(value='Σ All Instructors', id='Instructor-Dropdown')
        ], **globals.adaptiv_width_6),
    ]),
    dcc.Loading(
        id='loading-kpi-school',
        type='default',
        children=html.Div(
            dbc.Row([
            dbc.Col([
                dbc.Card([dbc.CardHeader("Instruction Hours"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Instruction-Hours-Trainee'),
                ]
            )
            ])
            ], **globals.adaptiv_width_3),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Trainings Sets"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Trainings-Sets-Trainee'),
                ]
            )
            ])
            ], **globals.adaptiv_width_3),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Instruction Hours"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Instruction-Hours-Instructor'),
                ]
            )
            ])
            ], **globals.adaptiv_width_3),
            dbc.Col([
                dbc.Card([dbc.CardHeader("Trainees"),
                dbc.CardBody(
                [
                    html.H4("XXX h", id='Number-of-Trainees'),
                ]
            )
            ])
            ], **globals.adaptiv_width_3),
        ], className="g-0"))),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Trainee Instruction Time Plot"),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-Trainee-Instruction-Time-Plot',
                                  type='cube',
                                  children=html.Div(
                                      dcc.Graph(id='Trainee-Instruction-Time-Plot'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_6),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instructor Instruction Time Plot"),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-Instructor-Instruction-Time-Plot',
                                  type='cube',
                                  children=html.Div(
                                      dcc.Graph(id='Instructor-Instruction-Time-Plot'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_6)
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("HeatMap Trainee"),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-HeatMap-Trainee',
                                  type='cube',
                                  children=html.Div(
                                      dcc.Graph(id='HeatMap-Trainee'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_6),
        dbc.Col([
            dbc.Card([dbc.CardHeader("HeatMap Instructor"),
                      dbc.CardBody(
                          [
                              dcc.Loading(
                                  id='loading-HeatMap-Instructor',
                                  type='cube',
                                  children=html.Div(
                                      dcc.Graph(id='HeatMap-Instructor'))),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_6)
    ], className="g-0")
])


@callback(Output('Trainee-Dropdown', 'options'),
          Input('instructorlog-store', 'data'),
          Input('date-picker-range', 'start_date'),
          Input('date-picker-range', 'end_date'))
def update_trainee_dropdown(instructorlog_dict, start_date, end_date):
    if instructorlog_dict is None:
        trainees = []
        trainees = np.append(trainees, 'Σ All Trainees')
        return trainees

    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    trainees = filtered_instructor_df['Pilot'].sort_values().unique()
    # Append 'Σ All Trainees' to the array of unique trainees names
    trainees = np.append(trainees, 'Σ All Trainees')

    return trainees

@callback(Output('Instructor-Dropdown', 'options'),
          Input('instructorlog-store', 'data'),
          Input('date-picker-range', 'start_date'),
          Input('date-picker-range', 'end_date'))
def update_instructor_dropdown(instructorlog_dict, start_date, end_date):
    if instructorlog_dict is None:
        instructors = []
        instructors = np.append(instructors, 'Σ All Instructors')
        return instructors

    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    instructors = filtered_instructor_df['Instructor'].sort_values().unique()
    # Append 'Σ All instructors' to the array of unique instructors names
    instructors = np.append(instructors, 'Σ All Instructors')

    return instructors

@callback(
    [Output('Instruction-Hours-Trainee', 'children'),
     Output('Trainings-Sets-Trainee', 'children')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Trainee-Dropdown', 'value')]
)
def update_trainee_header(instructorlog_dict, start_date, end_date, trainee_dropdown):
    if instructorlog_dict is None:
        instruction_hours_trainee, trainings_sets_trainee = ('NO DATA',) * 2
        return [instruction_hours_trainee, trainings_sets_trainee]
    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    agg_instructor_df = dp.trainee_aggregation(filtered_instructor_df)

    if trainee_dropdown == 'Σ All Trainees':
        agg_instructor_df = agg_instructor_df.iloc[:, 1:].sum().to_frame().T
    else:
        agg_instructor_df = agg_instructor_df[agg_instructor_df['Pilot']==trainee_dropdown]

    if len(agg_instructor_df)==1:
        # Pilots Flight Time
        instruction_hours_trainee = f'{agg_instructor_df.iloc[0]["Total_Duration"]:.1f} h'
        # Pilots Number of Flights
        trainings_sets_trainee = f'{agg_instructor_df.iloc[0]["Number_of_Instructions"]:.0f} #'
    else:
        instruction_hours_trainee, trainings_sets_trainee = ('NO DATA',) * 2

    return instruction_hours_trainee, trainings_sets_trainee


@callback(
    [Output('Instruction-Hours-Instructor', 'children'),
    Output('Number-of-Trainees', 'children'),],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Instructor-Dropdown', 'value')]
)
def update_instructor_header(instructorlog_dict, start_date, end_date, instructor_dropdown):
    if instructorlog_dict is None:
        instruction_hours_instructor, trainees_per_instructor = ('NO DATA',) * 2
        return [instruction_hours_instructor, trainees_per_instructor]
    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    agg_instructor_df = dp.instructor_aggregation(filtered_instructor_df)

    if instructor_dropdown == 'Σ All Instructors':
        agg_instructor_df = agg_instructor_df.iloc[:, 1:].sum().to_frame().T
    else:
        agg_instructor_df = agg_instructor_df[agg_instructor_df['Instructor']==instructor_dropdown]

    if len(agg_instructor_df)==1:
        # Pilots Flight Time
        instruction_hours_instructor = f'{agg_instructor_df.iloc[0]["Total_Duration"]:.1f} h'
        # Pilots Number of Flights
        trainees_per_instructor = f'{agg_instructor_df.iloc[0]["Number_of_Different_Pilots"]:.0f} #'
    else:
        instruction_hours_instructor, trainings_sets_instructor = ('NO DATA',) * 2

    return instruction_hours_instructor, trainees_per_instructor


@callback(
    [Output('Trainee-Instruction-Time-Plot', 'figure')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Trainee-Dropdown', 'value')]
)
def update_trainee_instruction_time_plot(instructorlog_dict, start_date, end_date, trainee_dropdown):
    if instructorlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)
    # Aggregate Pilots Data
    agg_trainee_df = dp.trainee_aggregation(filtered_instructor_df)
    # Create Pilot Plot
    trainee_instructor_time_plot = px.bar(
        agg_trainee_df,
        'Pilot',
        'Total_Duration',
        color='Total_Duration',
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale
    )
    # Update the color of the selected pilot in the bar plot
    if trainee_dropdown != 'Σ All Trainees':
        trainee_instructor_time_plot.update_traces(
            marker=dict(color=[globals.discrete_teal[-1]
                               if trainee == trainee_dropdown else globals.discrete_teal[0]
                               for trainee in agg_trainee_df['Pilot']]),
            hovertext=agg_trainee_df['Total_Duration'],
            selector=dict(type='bar')
        )
    trainee_instructor_time_plot.update(layout_coloraxis_showscale=False)
    trainee_instructor_time_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    trainee_instructor_time_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)

    return [trainee_instructor_time_plot]


@callback(
    [Output('Instructor-Instruction-Time-Plot', 'figure')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Instructor-Dropdown', 'value')]
)
def update_instructor_instruction_time_plot(instructorlog_dict, start_date, end_date, trainee_dropdown):
    if instructorlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)
    # Aggregate Pilots Data
    agg_trainee_df = dp.instructor_aggregation(filtered_instructor_df)
    # Create Pilot Plot
    trainee_instructor_time_plot = px.bar(
        agg_trainee_df,
        'Instructor',
        'Total_Duration',
        color='Total_Duration',
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale
    )
    # Update the color of the selected pilot in the bar plot
    if trainee_dropdown != 'Σ All Instructors':
        trainee_instructor_time_plot.update_traces(
            marker=dict(color=[globals.discrete_teal[-1]
                               if instructor == trainee_dropdown else globals.discrete_teal[0]
                               for instructor in agg_trainee_df['Instructor']]),
            hovertext=agg_trainee_df['Total_Duration'],
            selector=dict(type='bar')
        )
    trainee_instructor_time_plot.update(layout_coloraxis_showscale=False)
    trainee_instructor_time_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    trainee_instructor_time_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)

    return [trainee_instructor_time_plot]

@callback(
    [Output('HeatMap-Trainee', 'figure')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Trainee-Dropdown', 'value')]
)
def update_trainee_heatmap(instructorlog_dict, start_date, end_date, trainee_dropdown):
    if instructorlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    if trainee_dropdown != 'Σ All Trainees':
        filtered_instructor_df = filtered_instructor_df[filtered_instructor_df['Pilot']==trainee_dropdown]

    pivot_trainee_df = dp.heatmap_preparation(filtered_instructor_df, start_date, end_date, 'Duration')

    # Create Pilot Plot
    trainee_instructor_time_plot = px.imshow(
        pivot_trainee_df,
        x=pivot_trainee_df.columns,
        y=pivot_trainee_df.index,
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale
    )

    trainee_instructor_time_plot.update(layout_coloraxis_showscale=False)
    trainee_instructor_time_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)

    return [trainee_instructor_time_plot]


@callback(
    [Output('HeatMap-Instructor', 'figure')],
    [Input('instructorlog-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('Instructor-Dropdown', 'value')]
)
def update_instructor_heatmap(instructorlog_dict, start_date, end_date, instructor_dropdown):
    if instructorlog_dict is None:
        not_data_plot = plot.not_data_figure()
        return [not_data_plot]
    # reload dataframe form dict
    filtered_instructor_df = dp.reload_instructor_dataframe_from_dict(instructorlog_dict, start_date, end_date)

    if instructor_dropdown != 'Σ All Instructors':
        filtered_instructor_df = filtered_instructor_df[filtered_instructor_df['Instructor']==instructor_dropdown]

    pivot_instructor_df = dp.heatmap_preparation(filtered_instructor_df, start_date, end_date, 'Duration')

    # Create Pilot Plot
    instructor_instructor_time_plot = px.imshow(
        pivot_instructor_df,
        x=pivot_instructor_df.columns,
        y=pivot_instructor_df.index,
        template=globals.plot_template,
        color_continuous_scale=globals.color_scale
    )

    instructor_instructor_time_plot.update(layout_coloraxis_showscale=False)
    instructor_instructor_time_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)

    return [instructor_instructor_time_plot]