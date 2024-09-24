# Analytics page

# Libraries
from icecream import ic
import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import globals
import data_preparation as dp

globals.init()

dash.register_page(__name__, path='/analytics', name='Analytics')

layout = html.Div([
    html.H1('Analytics Tab'),
    # Select Data source (Flightlog, Instructorlog, Reservationlog, Member, Finance)
    dcc.Loading(id="loading-select-data-source", children=[
        dcc.Dropdown(id='dropdown-data-source', placeholder='Select Data Source')
    ]),
    # Card for Linear Regression, select two variables and one label
    dcc.Loading(id="loading-linear-regression", children=[
        dbc.Card([
            dbc.CardHeader('Linear Regression'),
            dbc.CardBody([
                html.H5('Select Variables'),
                dcc.Dropdown(id='dropdown-x-linear-regression', placeholder='Select X Variable'),
                dcc.Dropdown(id='dropdown-y-linear-regression', placeholder='Select Y Variable'),
                dcc.Dropdown(id='dropdown-label-linear-regression', placeholder='Select Label Variable'),
                html.Button('Run Linear Regression', id='button-run-linear-regression', n_clicks=0),
                html.Div(id='output-linear-regression')
            ])
        ])
    ]),
])

# Helper Function to load data from store into dataframe
def load_data_from_store(data_source, flightlog, instructorlog, reservationlog,\
                          member, finance, start_date, end_date):
    if data_source == 'flightlog':
        df = dp.reload_flightlog_dataframe_from_dict(flightlog, start_date, end_date)
        df = dp.pilot_aggregation(df)
    elif data_source == 'instructorlog':
        df = dp.reload_instructor_dataframe_from_dict(instructorlog, start_date, end_date)
    elif data_source == 'reservationlog':
        df = dp.reload_reservation_dataframe_from_dict(reservationlog, start_date, end_date)
    elif data_source == 'member':
        df = dp.reload_member_dataframe_from_dict(member, start_date, end_date)
    return df


# Callbacks
# Fill dropdown options with data sources that are not None
@callback(
    Output('dropdown-data-source', 'options'),
    [Input('flightlog-store', 'data'),
     Input('instructorlog-store', 'data'),
     Input('reservationlog-store', 'data'),
     Input('member-store', 'data'),
     Input('finance-store', 'data')]
)
def update_dropdown_data_source(flightlog, instructorlog, reservationlog, member, finance):
    data_sources = []
    if flightlog is not None:
        data_sources.append({'label': 'Flightlog', 'value': 'flightlog'})
    if instructorlog is not None:
        data_sources.append({'label': 'Instructorlog', 'value': 'instructorlog'})
    if reservationlog is not None:
        data_sources.append({'label': 'Reservationlog', 'value': 'reservationlog'})
    if member is not None:
        data_sources.append({'label': 'Member', 'value': 'member'})
    if finance is not None:
        data_sources.append({'label': 'Finance', 'value': 'finance'})
    return data_sources


# Fill dropdown options in Linear Regression Card with columns from selected data source
@callback(
    [Output('dropdown-x-linear-regression', 'options'),
     Output('dropdown-y-linear-regression', 'options'),
     Output('dropdown-label-linear-regression', 'options')],
    [Input('dropdown-data-source', 'value'),
     Input('flightlog-store', 'data'),
     Input('instructorlog-store', 'data'),
     Input('reservationlog-store', 'data'),
     Input('member-store', 'data'),
     Input('finance-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_dropdown_variables(data_source, flightlog_dict, instructorlog_dict, reservationlog_dict,\
                               member_dict, finance_dict, start_date, end_date):
    if data_source is None:
        return [], [], []
    else:
        # reload dataframe form dict
        df = load_data_from_store(data_source, flightlog_dict, instructorlog_dict,\
                                  reservationlog_dict, member_dict, finance_dict, start_date, end_date)
        return [{'label': col, 'value': col} for col in df.columns],\
            [{'label': col, 'value': col} for col in df.columns],\
            [{'label': col, 'value': col} for col in df.columns]


# Run Linear Regression an retrun plot
@callback(
    Output('output-linear-regression', 'children'),
    [Input('button-run-linear-regression', 'n_clicks'),
     Input('dropdown-x-linear-regression', 'value'),
     Input('dropdown-y-linear-regression', 'value'),
     Input('dropdown-label-linear-regression', 'value'),
     Input('dropdown-data-source', 'value'),
     Input('flightlog-store', 'data'),
     Input('instructorlog-store', 'data'),
     Input('reservationlog-store', 'data'),
     Input('member-store', 'data'),
     Input('finance-store', 'data'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def run_linear_regression(n_clicks, x, y, label, data_source, flightlog_dict, instructorlog_dict,\
                            reservationlog_dict, member_dict, finance_dict, start_date, end_date):
    if n_clicks == 0:
        return ''
    else:
        # reload dataframe form dict
        df = load_data_from_store(data_source, flightlog_dict, instructorlog_dict,\
                                  reservationlog_dict, member_dict, finance_dict, start_date, end_date)
        
        # Convert timedelta64 columns to total seconds
        if pd.api.types.is_timedelta64_dtype(df[x]):
            df[x] = df[x].dt.total_hours()
        if pd.api.types.is_timedelta64_dtype(df[y]):
            df[y] = df[y].dt.total_hours()
        if label and pd.api.types.is_timedelta64_dtype(df[label]):
            df[label] = df[label].dt.total_hours()
        
        # run linear regression
        linear_regression_plot = px.scatter(df, x=x, y=y, trendline='ols',
                                            trendline_scope="overall",
                                            color=label,
                                            template=globals.plot_template,
                                            color_continuous_scale=globals.color_scale)
        # Set fixed marker size
        linear_regression_plot.update_traces(marker=dict(size=20))
        linear_regression_plot.update(layout_coloraxis_showscale=False)
        linear_regression_plot.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
        linear_regression_plot.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
        linear_regression_plot.update_layout(margin=globals.plot_margin,
                                          paper_bgcolor=globals.paper_bgcolor,
                                          plot_bgcolor=globals.paper_bgcolor)
        n_clicks = 0
        return dcc.Graph(figure=linear_regression_plot)
