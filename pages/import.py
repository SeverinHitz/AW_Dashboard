# Intro page

# Libraries
from icecream import ic  # Debugging library for printing variable values
import dash  # Core Dash library
from dash import Dash, dcc, html, callback, Input, Output, dash_table, State  # Dash components for building web app UI
import dash_bootstrap_components as dbc  # Dash components styled with Bootstrap
import pandas as pd  # Data manipulation library
from datetime import datetime  # Library for handling dates and times
import base64  # Library for encoding/decoding data
import io  # Input/Output library for handling various types of I/O
import plotly.express as px  # Visualization library for creating interactive charts
# Import other Files
import data_preparation as dp  # Custom module for data preparation tasks
import globals  # Custom module for global variables and settings

globals.init()  # Initialize global variables

# --------------------------------------- Text --------------------------------------------------

# Requirements Section: Defines the data requirements for the application
requirement_header = [
    html.Thead(html.Tr([html.Th("Data Source"), html.Th("Overview"), html.Th("Pilot"),
                        html.Th("Aircraft"), html.Th("School"),
                        html.Th("Member"), html.Th("Finance"), html.Th("Analytics")]))
]

data_requirement = [
    ["Flightlog", "x", "x", "x", "x", "", "", "(x)"],
    ["Instructorlog", "x", "", "", "x", "", "", "(x)"],
    ["Reservationlog", "", "x", "", "", "", "", "(x)"],
    ["Member", "", "", "", "", "x", "", "(x)"],
    ["Finance", "", "", "", "", "", "x", "(x)"]
]

requirement_body = [html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in data_requirement])]

# Creates a Bootstrap table component with the data requirements
table_requirement = dbc.Table(requirement_header + requirement_body, bordered=True,
                              style={'font-size': 'smaller', 'padding': '1px', 'border-collapse': 'collapse'})

# Security Section: Provides information on data security and privacy
security_text = ('This website is designed for the analysis of Airmanager data. Please note that the data is\
 not retained on the server. Instead, it\'s temporarily held in your browser\'s Web Storage during your session.\
  The information stored locally includes first name, surname, and but not in combination with postcode, and date of birth.\
   It\'s ensured that all other personal details are removed right at the beginning of the process.\
    However, for the purpose of data selection, the complete dataset is transmitted to the server once.\
     All transfer\'s are conducted over a secure HTTPS connection. Despite this security measure, it\'s highly\
      advised to remove or anonymize any highly sensitive information, such as email addresses, phone numbers,\
       and bank details (IBAN, etc.), before uploading the data.')

disclosure_text = 'No liability is accepted for the data and users must ensure that they operate within the\
 organisation\'s own privacy policy'

# Data Format Section: Describes the required data format for uploads
format_header = [
    html.Thead(html.Tr([html.Th("Dataset"), html.Th("Required Columns")]))
]

data_format = [
    ["Flightlog", "'Datum', 'Vorname', 'Name', 'Abflugort', 'Ankunftsort', 'FlugzeitFlugzeit',\
         'Block Zeit', 'Benzin', 'Öl', 'Landungen', 'Flugart', 'Flugzeug'"],
    ["Instructorlog", "'Datum', 'Pilot Vorname', 'Pilot Name', 'Fluglehrer Vorname', 'Fluglehrer Name', 'Dauer'"],
    ["Reservationlog", "'Von', 'Bis', 'Vorname', 'Name', 'Flugzeug', 'Typ', 'Gelöscht', 'Löschgrund'"],
    ["Member", "'AirManager ID', 'PLZ', 'Geburtsdatum', 'Mitgliedschaft', 'Eintrittsdatum'"],
    ["Finance", ""]
]

format_body = [html.Tbody([html.Tr([html.Td(cell) for cell in row]) for row in data_format])]

# Creates a Bootstrap table component for the data format requirements
table_format = dbc.Table(format_header + format_body, bordered=True,
                              style={'font-size': 'smaller', 'padding': '1px', 'border-collapse': 'collapse'})

# Register the page with Dash, setting the path and name
dash.register_page(__name__, path='/', name='Import')

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Instructions"),
            dbc.CardBody(
            [
                html.P("1. Download the data from Airmanager."),
                html.P(
                    "2. Upload the data by dragging and dropping it into the respective fields below,\
                     following data is required per page:"),
                table_requirement,
                html.P("3. Make sure data Structure matches the list Below."),
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
                      dbc.CardFooter(
                          dcc.Loading(
                          id='loading-flightlog',
                          type='dot',
                          children=html.Div(id='flightlog-upload-status'))),
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
                      dbc.CardFooter(
                          dcc.Loading(
                          id='loading-instructorlog',
                          type='dot',
                          children=html.Div(id='instructorlog-upload-status'))),
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
                      dbc.CardFooter(
                          dcc.Loading(
                          id='loading-reservationlog',
                          type='dot',
                          children=html.Div(id='reservationlog-upload-status'))),
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
                      dbc.CardFooter(
                          dcc.Loading(
                              id='loading-member',
                              type='dot',
                              children=html.Div(id='member-upload-status'))),
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
                      dcc.Loading(
                          id='loading-member',
                          type='dot',
                          children=html.Div(
                              dbc.CardBody(
                          [
                              html.Div(id='flightlog-store-status'),
                              html.Div(id='instructorlog-store-status'),
                              html.Div(id='reservationlog-store-status'),
                              html.Div(id='member-store-status'),
                              html.Div(id='finance-store-status'),
                          ]
                      )))
                      ])
        ], **globals.adaptiv_width_2),
    ], className="g-0"),
    dbc.Row([
        dbc.Col([
            dbc.Card([dbc.CardHeader("Data Requirements / Format"),
            dbc.CardBody(
            [
                html.P([html.B("Data Size Limitation:"),
                        " Please note, depending on your device (mobile or desktop),\
                 the data size should only be between 5-10 MB."]),
                html.P([html.B("Data Format and Source:"),
                        " The data should be a direct export from AirManager or an Excel file in the .xlsx format."]),
                html.P([html.B("Required Data:")]),
                table_format
            ]
        )
        ])
        ], **globals.adaptiv_width_12),
    ], className="g-0"),
])


def parse_contents(contents, filename):
    '''
    Function that loads the File into a Dataframe. Can handle a .xlsx File with correct Datetime Formats and direct
    Export form Airmanager which is an HTML Table with .xls Ending. In this case the datetime Formats will be initialised
    :param contents: File Upload
    :param filename: Name of File
    :return: Status (bool), Dataframe, Error Text, Text Style
    '''
    ic(filename)
    # When no File was uploaded
    if not contents:
        return False, None, f'No new File submitted', {'color':'yellow'}  # No File Text

    allowed_suffixes = ['.xlsx', '.xls']
    # Check Ending
    if not any(filename.endswith(suffix) for suffix in allowed_suffixes):
        return False, None, f'Not a Excel File (.xlsx)', {'color':'red'}  # Wrong File type Text

    # Decode Contentstring
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Try loading File into Pandas (if not returns None)
    try:
        if filename.endswith('.xlsx'):  # When its a new Excel File -> Correct Date Time Columns
            df = pd.read_excel(io.BytesIO(decoded))
        if filename.endswith('.xls'):  # When its a direct Export form Airmanager in the old Excel Format
            # Advise File is actually a HTML Table with a .xls Ending not a Excel File
            dataframes = pd.read_html(io.BytesIO(decoded), header=0)
            df = dataframes[0]  # Select first Dataframe (only one)
            df = dp.xls_format_cleanup(df) # Call Function for Datetime init
    except Exception as e:  # Catch any other Error
        ic(e)
        return False, None, f'Could not read Content', {'color':'red'}

    return True, df, f'File loaded', {'color':'lightgreen'} # Return Dataframe and Checktext


# Callback that handles the Flighlog Data
@callback(Output('flightlog-store', 'data'), # Flightlog Data as Dict
            Output('flightlog-store-date', 'data'), # Date of File uploaded (last edited)
            Output('flightlog-upload-status', 'children'), # Status of File (str)
            Output('flightlog-upload-status','style'), # Status Text color
            Input('flightlog-upload', 'contents'), # Upload File (content)
            State('flightlog-upload', 'filename'), # Upload Filename
            State('flightlog-upload', 'last_modified'), # File Last Edited
            State('flightlog-store', 'data'), # Old Date to reinstate
            State('flightlog-store-date', 'data')) # old Data Date to reinstate
def upload_flightlog_data(flightlog_upload, flightlog_filename, flightlog_last_modified, old_data, old_data_date):
    # Try load Dataframe
    status, df, string, style = parse_contents(flightlog_upload, flightlog_filename) # Call Function to parse Content
    if status:  # If Status True (parse worked)
        try:  # Try cleanup Process
            df = dp.data_cleanup_flightlog(df)  # call cleanup Function
        except Exception as e:  # If cleanup don't work
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason and retain old data and date
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(flightlog_last_modified)  # Get Timestamp from File
    formatted_date = timestamp.strftime('%d.%m.%Y')  # Extract Date
    df_as_dict = df.to_dict('records')  # convert DF as Dictionary to be able to Save in Web Storage API
    return df_as_dict, formatted_date, f'File {flightlog_filename} last modified {timestamp}', style


# Instructorlog Data Import Function
@callback(Output('instructorlog-store', 'data'),  # Instructor Data as Dict
            Output('instructorlog-store-date', 'data'),  # Date of File uploaded (last edited)
            Output('instructorlog-upload-status', 'children'),  # Status of File (str)
            Output('instructorlog-upload-status','style'),  # Status Text color
            Input('instructorlog-upload', 'contents'),  # Upload File (content)
            State('instructorlog-upload', 'filename'),  # Upload Filename
            State('instructorlog-upload', 'last_modified'),  # File Last Edited
            State('instructorlog-store', 'data'),  # Old Date to reinstate
            State('instructorlog-store-date', 'data'))  # old Data Date to reinstate
def upload_instructorlog_data(instructorlog_upload, instructorlog_filename, instructorlog_last_modified, old_data, old_data_date):
     # Try load Dataframe
    status, df, string, style = parse_contents(instructorlog_upload, instructorlog_filename)  # Call Function to parse Content
    # Try Clean up
    if status:  # If Status True (parse worked)
        try:  # Try cleanup Process
            df = dp.data_cleanup_instructorlog(df)  # call cleanup Function
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason and retain old data and date
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(instructorlog_last_modified)  # Get Timestamp from File
    formatted_date = timestamp.strftime('%d.%m.%Y')  # Extract Date
    df_as_dict = df.to_dict('records')  # convert DF as Dictionary to be able to Save in Web Storage API
    return df_as_dict, formatted_date, f'File {instructorlog_filename} last modified {timestamp}', style


# reservationlog Data Import Function
@callback(Output('reservationlog-store', 'data'),  # Reservation Data as Dict
            Output('reservationlog-store-date', 'data'),  # Date of File uploaded (last edited)
            Output('reservationlog-upload-status', 'children'),  # Status of File (str)
            Output('reservationlog-upload-status','style'),  # Status Text color
            Input('reservationlog-upload', 'contents'),  # Upload File (content)
            State('reservationlog-upload', 'filename'),  # Upload Filename
            State('reservationlog-upload', 'last_modified'),  # File Last Edited
            State('reservationlog-store', 'data'),  # Old Date to reinstate
            State('reservationlog-store-date', 'data'))  # old Data Date to reinstate
def upload_reservationlog_data(reservationlog_upload, reservationlog_filename, reservationlog_last_modified, old_data, old_data_date):
    # Try load Dataframe
    status, df, string, style = parse_contents(reservationlog_upload, reservationlog_filename)  # Call Function to parse Content

    # Try Clean up
    if status:  # If Status True (parse worked)
        try:  # Try cleanup Process
            df = dp.data_cleanup_reservation(df)  # call cleanup Function
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

    # If conversion to df Failed print Reason and retain old data and date
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(reservationlog_last_modified)  # Get Timestamp from File
    formatted_date = timestamp.strftime('%d.%m.%Y')  # Extract Date
    df_as_dict = df.to_dict('records')  # convert DF as Dictionary to be able to Save in Web Storage API
    return df_as_dict, formatted_date, f'File {reservationlog_filename} last modified {timestamp}', style


# member Data Import Function
@callback(Output('member-store', 'data'),  # Member Data as Dict
            Output('member-store-date', 'data'),  # Date of File uploaded (last edited)
            Output('member-upload-status', 'children'),  # Status of File (str)
            Output('member-upload-status','style'),  # Status Text color
            Input('member-upload', 'contents'),  # Upload File (content)
            State('member-upload', 'filename'),  # Upload Filename
            State('member-upload', 'last_modified'),  # File Last Edited
            State('member-store', 'data'),  # Old Date to reinstate
            State('member-store-date', 'data'))  # old Data Date to reinstate
def upload_member_data(member_upload, member_filename, member_last_modified, old_data, old_data_date):
    # Try load Dataframe
    status, df, string, style = parse_contents(member_upload, member_filename)  # Call Function to parse Content
    # Try Clean up
    if status:  # If Status True (parse worked)
        try:  # Try cleanup Process
            df = dp.data_cleanup_member(df)  # call cleanup Function
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

     # If conversion to df Failed print Reason and retain old data and date
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(member_last_modified)  # Get Timestamp from File
    formatted_date = timestamp.strftime('%d.%m.%Y')  # Extract Date
    df_as_dict = df.to_dict('records')  # convert DF as Dictionary to be able to Save in Web Storage API
    return df_as_dict, formatted_date, f'File {member_filename} last modified {timestamp}', style

# Finance Data Import Function
@callback(Output('finance-store', 'data'),  # Finance Data as Dict
            Output('finance-store-date', 'data'),  # Date of File uploaded (last edited)
            Output('finance-upload-status', 'children'),  # Status of File (str)
            Output('finance-upload-status','style'),  # Status Text color
            Input('finance-upload', 'contents'),  # Upload File (content)
            State('finance-upload', 'filename'),  # Upload Filename
            State('finance-upload', 'last_modified'),  # File Last Edited
            State('finance-store', 'data'),  # Old Date to reinstate
            State('finance-store-date', 'data'))  # old Data Date to reinstate
def upload_member_data(member_upload, member_filename, member_last_modified, old_data, old_data_date):
     # Not Supported yet:
    if True:  # Delete as soon as implemented
        status, df, string, style = False, None, f'Not yet supported', {'color': 'orange'}
        return status, df, string, style
     # Try load Dataframe
    status, df, string, style = parse_contents(member_upload, member_filename)  # Call Function to parse Content
     # Try Clean up
    if status:  # If Status True (parse worked)
        try:  # Try cleanup Process
            df = dp.data_cleanup_member(df)  # call cleanup Function
        except Exception as e:
            ic(e)
            status, df, string, style = False, None, f'Columns do not match expectations', {'color':'red'}

     # If conversion to df Failed print Reason and retain old data and date
    if not status:
            return old_data, old_data_date, string, style

    timestamp = datetime.fromtimestamp(member_last_modified)  # Get Timestamp from File
    formatted_date = timestamp.strftime('%d.%m.%Y')  # Extract Date
    df_as_dict = df.to_dict('records')  # convert DF as Dictionary to be able to Save in Web Storage API
    return df_as_dict, formatted_date, f'File {member_filename} last modified {timestamp}', style

# Callback for Data Status section
@callback(Output('flightlog-store-status', 'children'),  # Flightlog Status Text
          Output('instructorlog-store-status', 'children'),  # Instructorlog Status Text
          Output('reservationlog-store-status', 'children'),  # Reservationslog Status Text
          Output('member-store-status', 'children'),  # Member Status Text
          Output('flightlog-store-status', 'style'),  # Flightlog Text Style
          Output('instructorlog-store-status', 'style'),  # Instructorlog Text Style
          Output('reservationlog-store-status', 'style'),  # Reservationslog Text Style
          Output('member-store-status', 'style'),  # Member Status Text Style
          Input('flightlog-store', 'data'),  # Flightlog Data
          Input('flightlog-store-date', 'data'),  # Flightlog Data Date
          Input('instructorlog-store', 'data'),  # Instructorlog Data
          Input('instructorlog-store-date', 'data'),  # Instructorlog Data Date
          Input('reservationlog-store', 'data'),  # Reservationlog Data
          Input('reservationlog-store-date', 'data'),  # Reservationslog Data Date
          Input('member-store', 'data'),  # Member Data
          Input('member-store-date', 'data'),  # Member Data Date
          )
def check_status_of_data(flightlog_store, flightlog_store_date,
                         instructorlog_store, instructorlog_store_date,
                         reservationlog_store, reservationlog_store_date,
                         member_store, member_store_date):
    if flightlog_store is None:  # Check if Flightlog Data is available
        flightlog_msg = f'No Flightlog Data'
        flightlog_style = {'color': 'red'}
    else:
        flightlog_msg = f'Flightlog {flightlog_store_date}'
        flightlog_style = {'color': 'lightgreen'}

    if instructorlog_store is None:  # Check if Instructor Data is available
        instructorlog_msg = f'No Instructorlog Data'
        instructorlog_style = {'color': 'red'}
    else:
        instructorlog_msg = f'Instructorlog {instructorlog_store_date}'
        instructorlog_style = {'color': 'lightgreen'}

    if reservationlog_store is None:  # Check if Reservationslog Data is available
        reservationlog_msg = f'No Reservationlog Data'
        reservationlog_style = {'color': 'red'}
    else:
        reservationlog_msg = f'Reservationlog {reservationlog_store_date}'
        reservationlog_style = {'color': 'lightgreen'}

    if member_store is None:  # Check if Member Data is available
        member_msg = f'No Member Data'
        member_style = {'color': 'red'}
    else:
        member_msg = f'Member {member_store_date}'
        member_style = {'color': 'lightgreen'}

    return (flightlog_msg, instructorlog_msg, reservationlog_msg, member_msg,
            flightlog_style, instructorlog_style, reservationlog_style, member_style)
