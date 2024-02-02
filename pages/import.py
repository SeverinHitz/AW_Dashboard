# Intro page

# Libraries
from icecream import ic
import dash
from dash import Dash, dcc, html, callback, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import base64
import io
import plotly.express as px
# Import other Files
import data_preparation as dp
import globals

globals.init()

# --------------------------------------- Text --------------------------------------------------
table_header = [
    html.Thead(html.Tr([html.Th("Data Source"), html.Th("Overview"), html.Th("Pilot"),
                        html.Th("Aircraft"), html.Th("School"),
                        html.Th("Member"), html.Th("Finance"), html.Th("Analytics")]))
]

# Sample data
data = [
    ["Flightlog", "x", "x", "x", "x", "", "", "(x)"],
    ["Instructorlog", "x", "", "", "x", "", "", "(x)"],
    ["Reservationlog", "", "x", "", "", "", "", "(x)"],
    ["Member", "", "", "", "", "x", "", "(x)"],
    ["Finance", "", "", "", "", "", "x", "(x)"]
]

table_body = [html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in data])]

table = dbc.Table(table_header + table_body, bordered=True, style={'font-size': 'smaller', 'padding': '1px'})

security_text = 'This website is intended for analysing Airmanager data. The data is not\
 stored on the server but locally in the browser session. This stored data includes the following\
  personal data: First name, surname, postcode and date of birth. All other personal data\
   is discarded during initialisation. However, it is sent once to the server for data selection during upload.\
    This connection is made via a secure https connection. It is still recommended to delete columns\
     with highly sensitive data before they are uploaded (e.g. e-mail, telephone number, IBAN etc.).'

disclosure_text ='No liability is accepted for the data and users must ensure that they operate within the\
 organisation\'s own privacy policy'

dash.register_page(__name__, path='/', name='Import')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instructions"),
            dbc.CardBody(
            [
                html.P("1. Download the data from Airmanager."),
                html.P(
                    "2. Upload the data by dragging and dropping it into the respective fields, following data is required per page:"),
                table
            ]
        )
        ])
        ], **globals.adaptiv_width_7),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Data Security / Privacy"),
            dbc.CardBody(
            [
                html.P(security_text),
                html.P(disclosure_text),
                html.A("More about Web Storage API",
                       href="https://www.ramotion.com/blog/what-is-web-storage/"),
                html.Br(),
                html.A("GitHub Page", href="https://github.com/SeverinHitz"),
                html.Br(),
                html.A("Airmanager", href= "https://airmanager.ch/"),
            ]
        )
        ])
        ], **globals.adaptiv_width_5),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Flightlog"),
                      dbc.CardBody(
                          [
                            dcc.Upload(
                                id='flightlog-upload',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select Files')
                                ]),
                                style={
                                    'width': '100%',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center'
                                },
                                # Allow multiple files to be uploaded
                                multiple=False
                            ),
                          ]
                      ),
                      dbc.CardFooter(id='flightlog-upload-status'),
                      ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instructorlog"),
                      dbc.CardBody(
                          [
                              dcc.Upload(
                                  id='instructorlog-upload',
                                  children=html.Div([
                                      'Drag and Drop or ',
                                      html.A('Select Files')
                                  ]),
                                  style={
                                      'width': '100%',
                                      'lineHeight': '60px',
                                      'borderWidth': '1px',
                                      'borderStyle': 'dashed',
                                      'borderRadius': '5px',
                                      'textAlign': 'center'
                                  },
                                  # Allow multiple files to be uploaded
                                  multiple=False
                              ),
                          ]
                      ),
                      dbc.CardFooter(id='instructorlog-upload-status'),
                      ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Reservationlog"),
                      dbc.CardBody(
                          [
                              dcc.Upload(
                                  id='reservationlog-upload',
                                  children=html.Div([
                                      'Drag and Drop or ',
                                      html.A('Select Files')
                                  ]),
                                  style={
                                      'width': '100%',
                                      'lineHeight': '60px',
                                      'borderWidth': '1px',
                                      'borderStyle': 'dashed',
                                      'borderRadius': '5px',
                                      'textAlign': 'center'
                                  },
                                  # Allow multiple files to be uploaded
                                  multiple=False
                              ),
                          ]
                      ),
                      dbc.CardFooter(id='reservationlog-upload-status'),
                      ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Members"),
                      dbc.CardBody(
                          [
                              dcc.Upload(
                                  id='member-upload',
                                  children=html.Div([
                                      'Drag and Drop or ',
                                      html.A('Select Files')
                                  ]),
                                  style={
                                      'width': '100%',
                                      'lineHeight': '60px',
                                      'borderWidth': '1px',
                                      'borderStyle': 'dashed',
                                      'borderRadius': '5px',
                                      'textAlign': 'center'
                                  },
                                  # Allow multiple files to be uploaded
                                  multiple=False
                              ),
                          ]
                      ),
                      dbc.CardFooter(id='member-upload-status'),
                      ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Finance"),
                      dbc.CardBody(
                          [
                              dcc.Upload(
                                  id='finance-upload',
                                  children=html.Div([
                                      'Drag and Drop or ',
                                      html.A('Select Files')
                                  ]),
                                  style={
                                      'width': '100%',
                                      'lineHeight': '60px',
                                      'borderWidth': '1px',
                                      'borderStyle': 'dashed',
                                      'borderRadius': '5px',
                                      'textAlign': 'center'
                                  },
                                  # Allow multiple files to be uploaded
                                  multiple=False
                              ),
                          ]
                      ),
                      dbc.CardFooter(id='finance-upload-status'),
                      ])
        ], **globals.adaptiv_width_2),
        dbc.Col([
            dbc.Card([dbc.CardHeader("Data Status"),
                      dbc.CardBody(
                          [
                              html.Div(id='flightlog-store-status'),
                              html.Div(id='instructorlog-store-status'),
                              html.Div(id='reservationlog-store-status'),
                              html.Div(id='member-store-status'),
                              html.Div(id='finance-store-status'),
                          ]
                      )
                      ])
        ], **globals.adaptiv_width_2),
    ], className="g-0")
])


def parse_contents(contents, filename):
    ic(filename)
    # When no File was uploaded
    if not contents:
        return False, None, f'No new File submitted', {'color':'yellow'}

    allowed_suffixes = ['.xlsx', '.xls']
    # Check Ending
    if not any(filename.endswith(suffix) for suffix in allowed_suffixes):
        return False, None, f'Not a Excel File (.xlsx)', {'color':'red'}

    # Decode Contentstring
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Try loading File into Pandas (if not returns None)
    try:
        if filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(decoded))
        if filename.endswith('.xls'):
            dataframes = pd.read_html(io.BytesIO(decoded), header=0)
            df = dataframes[0]
            df = dp.xls_format_cleanup(df)
    except Exception as e:
        ic(e)
        return False, None, f'Could not read Content', {'color':'red'}

    return True, df, f'File loaded', {'color':'lightgreen'}

# Flightlog Data

@callback(Output('flightlog-store', 'data'),
            Output('flightlog-store-date', 'data'),
            Output('flightlog-upload-status', 'children'),
            Output('flightlog-upload-status','style'),
            Input('flightlog-upload', 'contents'),
            State('flightlog-upload', 'filename'),
            State('flightlog-upload', 'last_modified'),
            State('flightlog-store', 'data'),
            State('flightlog-store-date', 'data'))
def upload_flightlog_data(flightlog_upload, flightlog_filename, flightlog_last_modified, old_data, old_data_date):
    # Try load Dataframe
    status, df, string, style = parse_contents(flightlog_upload, flightlog_filename)
    if status:
        try:
            df = dp.data_cleanup_flightlog(df)
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(flightlog_last_modified)
    formatted_date = timestamp.strftime('%d.%m.%Y')
    df_as_dict = df.to_dict('records')
    return df_as_dict, formatted_date, f'File {flightlog_filename} last modified {timestamp}', style


# Instructorlog Data
@callback(Output('instructorlog-store', 'data'),
            Output('instructorlog-store-date', 'data'),
            Output('instructorlog-upload-status', 'children'),
            Output('instructorlog-upload-status','style'),
            Input('instructorlog-upload', 'contents'),
            State('instructorlog-upload', 'filename'),
            State('instructorlog-upload', 'last_modified'),
            State('instructorlog-store', 'data'),
            State('instructorlog-store-date', 'data'))
def upload_instructorlog_data(instructorlog_upload, instructorlog_filename, instructorlog_last_modified, old_data, old_data_date):
    # Try load Dataframe
    status, df, string, style = parse_contents(instructorlog_upload, instructorlog_filename)
    # Try Clean up
    if status:
        try:
            df = dp.data_cleanup_instructorlog(df)
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(instructorlog_last_modified)
    formatted_date = timestamp.strftime('%d.%m.%Y')
    df_as_dict = df.to_dict('records')
    return df_as_dict, formatted_date, f'File {instructorlog_filename} last modified {timestamp}', style


# reservationlog Data
@callback(Output('reservationlog-store', 'data'),
            Output('reservationlog-store-date', 'data'),
            Output('reservationlog-upload-status', 'children'),
            Output('reservationlog-upload-status','style'),
            Input('reservationlog-upload', 'contents'),
            State('reservationlog-upload', 'filename'),
            State('reservationlog-upload', 'last_modified'),
            State('reservationlog-store', 'data'),
            State('reservationlog-store-date', 'data'))
def upload_reservationlog_data(reservationlog_upload, reservationlog_filename, reservationlog_last_modified, old_data, old_data_date):
    # Try load Dataframe
    status, df, string, style = parse_contents(reservationlog_upload, reservationlog_filename)

    # Try Clean up
    if status:
        try:
            df = dp.data_cleanup_reservation(df)
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(reservationlog_last_modified)
    formatted_date = timestamp.strftime('%d.%m.%Y')
    df_as_dict = df.to_dict('records')
    return df_as_dict, formatted_date, f'File {reservationlog_filename} last modified {timestamp}', style


# member Data
@callback(Output('member-store', 'data'),
            Output('member-store-date', 'data'),
            Output('member-upload-status', 'children'),
            Output('member-upload-status','style'),
            Input('member-upload', 'contents'),
            State('member-upload', 'filename'),
            State('member-upload', 'last_modified'),
            State('member-store', 'data'),
            State('member-store-date', 'data'))
def upload_member_data(member_upload, member_filename, member_last_modified, old_data, old_data_date):
    # Try load Dataframe
    status, df, string, style = parse_contents(member_upload, member_filename)
    # Try Clean up
    if status:
        try:
            df = dp.data_cleanup_member(df)
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(member_last_modified)
    formatted_date = timestamp.strftime('%d.%m.%Y')
    df_as_dict = df.to_dict('records')
    return df_as_dict, formatted_date, f'File {member_filename} last modified {timestamp}', style

# Finance Data
@callback(Output('finance-store', 'data'),
            Output('finance-store-date', 'data'),
            Output('finance-upload-status', 'children'),
            Output('finance-upload-status','style'),
            Input('finance-upload', 'contents'),
            State('finance-upload', 'filename'),
            State('finance-upload', 'last_modified'),
            State('finance-store', 'data'),
            State('finance-store-date', 'data'))
def upload_member_data(member_upload, member_filename, member_last_modified, old_data, old_data_date):
    # Not Supported yet:
    if True:
        status, df, string, style = False, None, f'Not yet supported', {'color': 'orange'}
        return status, df, string, style
    # Try load Dataframe
    status, df, string, style = parse_contents(member_upload, member_filename)
    # Try Clean up
    if status:
        try:
            df = dp.data_cleanup_member(df)
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(member_last_modified)
    formatted_date = timestamp.strftime('%d.%m.%Y')
    df_as_dict = df.to_dict('records')
    return df_as_dict, formatted_date, f'File {member_filename} last modified {timestamp}', style


@callback(Output('flightlog-store-status', 'children'),
          Output('instructorlog-store-status', 'children'),
          Output('reservationlog-store-status', 'children'),
          Output('member-store-status', 'children'),
          Output('flightlog-store-status', 'style'),
          Output('instructorlog-store-status', 'style'),
          Output('reservationlog-store-status', 'style'),
          Output('member-store-status', 'style'),
          Input('flightlog-store', 'data'),
          Input('flightlog-store-date', 'data'),
          Input('instructorlog-store', 'data'),
          Input('instructorlog-store-date', 'data'),
          Input('reservationlog-store', 'data'),
          Input('reservationlog-store-date', 'data'),
          Input('member-store', 'data'),
          Input('member-store-date', 'data'),
          )
def check_status_of_data(flightlog_store, flightlog_store_date,
                         instructorlog_store, instructorlog_store_date,
                         reservationlog_store, reservationlog_store_date,
                         member_store, member_store_date):
    if flightlog_store is None:
        flightlog_msg = f'No Flightlog Data'
        flightlog_style = {'color': 'red'}
    else:
        flightlog_msg = f'Flightlog {flightlog_store_date}'
        flightlog_style = {'color': 'lightgreen'}

    if instructorlog_store is None:
        instructorlog_msg = f'No Instructorlog Data'
        instructorlog_style = {'color': 'red'}
    else:
        instructorlog_msg = f'Instructorlog {instructorlog_store_date}'
        instructorlog_style = {'color': 'lightgreen'}

    if reservationlog_store is None:
        reservationlog_msg = f'No Reservationlog Data'
        reservationlog_style = {'color': 'red'}
    else:
        reservationlog_msg = f'Reservationlog {reservationlog_store_date}'
        reservationlog_style = {'color': 'lightgreen'}

    if member_store is None:
        member_msg = f'No Member Data'
        member_style = {'color': 'red'}
    else:
        member_msg = f'Member {member_store_date}'
        member_style = {'color': 'lightgreen'}

    return (flightlog_msg, instructorlog_msg, reservationlog_msg, member_msg,
            flightlog_style, instructorlog_style, reservationlog_style, member_style)
