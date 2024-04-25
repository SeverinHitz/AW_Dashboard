# Import necessary libraries
import pandas as pd
from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc
from datetime import datetime
import logging
from icecream import ic

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(message)s')

# Import other files
import data_preparation as dp
import globals

# Initialize global variables
globals.init()

# Path to logo image
logo_path = "assets/AirStats_Breit.png"

# Define start and end dates for date picker range
end_date = datetime.now()
start_date = end_date - pd.DateOffset(months=3)

# Initialize Dash app
app = Dash(__name__, pages_folder='pages', use_pages=True, external_stylesheets=[globals.stylesheet])
server = app.server  # When deployed

# Define layout of the app
app.layout = html.Div([
    html.Div([
        # Stores for session data
        dcc.Store(id='flightlog-store', storage_type='session'),
        dcc.Store(id='instructorlog-store', storage_type='session'),
        dcc.Store(id='reservationlog-store', storage_type='session'),
        dcc.Store(id='member-store', storage_type='session'),
        dcc.Store(id='finance-store', storage_type='session'),
        dcc.Store(id='flightlog-store-date', storage_type='session'),
        dcc.Store(id='instructorlog-store-date', storage_type='session'),
        dcc.Store(id='reservationlog-store-date', storage_type='session'),
        dcc.Store(id='member-store-date', storage_type='session'),
        dcc.Store(id='finance-store-date', storage_type='session'),
        dcc.Store(id='trend-switch', storage_type='session')
    ]),
    html.Div([
        # Navigation bar
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink('Import', href='/')),
                dbc.NavItem(dbc.NavLink('Overview', href='/overview')),
                dbc.NavItem(dbc.NavLink('Pilot', href='/pilot')),
                dbc.NavItem(dbc.NavLink('Aircraft', href='/aircraft')),
                dbc.NavItem(dbc.NavLink('School', href='/school')),
                dbc.NavItem(dbc.NavLink('Member', href='/member')),
                dbc.NavItem(dbc.NavLink('Finance', href='/finance')),
                dbc.NavItem(dbc.NavLink('Analytics', href='/analytics')),
                # dcc.RadioItems(['last Year', 'last Periode'], 'last Year'),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=start_date,
                    end_date=end_date,
                    display_format='DD.MM.YYYY'
                ),
            ],
            brand=html.Img(src=logo_path, height='40px'),
            brand_href='/',
            color='primary',
            dark=True,
            expand='lg',
        ),
    ]),
    page_container
])

# Run the app if this script is being executed directly
if __name__ == '__main__':
    app.run_server(debug=False)
