
# Import Libraries
import pandas as pd
from dash import Dash, html, dcc, page_container
import dash_bootstrap_components as dbc
from datetime import datetime
from icecream import ic
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(message)s')

# Import other Files
import data_preparation as dp
import globals

globals.init()

# Images
logo_path = "assets/AW_Logo_breit.png"


end_date = datetime.now()
start_date = end_date - pd.DateOffset(months=3)

#################################### App Section ##################################################

app = Dash(__name__, pages_folder='pages', use_pages=True, external_stylesheets=[globals.stylesheet])
server = app.server # When deployed

app.layout = html.Div([
    html.Div([
        dcc.Store(id='flightlog-store', storage_type='session'),
        dcc.Store(id='instructorlog-store', storage_type='session'),
        dcc.Store(id='reservationlog-store', storage_type='session'),
        dcc.Store(id='member-store', storage_type='session'),
        dcc.Store(id='finance-store', storage_type='session'),
        dcc.Store(id='flightlog-store-date', storage_type='session'),
        dcc.Store(id='instructorlog-store-date', storage_type='session'),
        dcc.Store(id='reservationlog-store-date', storage_type='session'),
        dcc.Store(id='member-store-date', storage_type='session'),
        dcc.Store(id='finance-store-date', storage_type='session')
    ]),
    html.Div([
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
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=start_date,
                    end_date=end_date,
                    display_format='DD.MM.YYYY'
                ),
            ],
            brand=html.Img(src=logo_path, height='35px'),
            brand_href='/',
            color='primary',
            dark=True,
        ),
    ]),
    page_container
])




if __name__ == '__main__':
    # Run app
    app.run_server(debug=False)
