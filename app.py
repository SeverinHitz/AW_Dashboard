import dash
# Import Libraries
import pandas as pd
from datetime import timedelta, date
from dash import Dash, dcc, html, dcc, callback, Input, Output, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
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

# Images
logo_path = "assets/AW_Logo_breit.png"


# Time select
# Path
flightlog_file = '240113_flightlog.xlsx'
flight_df = dp.load_data(flightlog_file)
# clean up
flight_df = dp.data_cleanup_flightlog(flight_df)
end_date = flight_df['Date'].max()
start_date = end_date - pd.DateOffset(months=3)

#################################### App Section ##################################################

app =  Dash(__name__, pages_folder='pages', use_pages=True, external_stylesheets=[stylesheet])

app.layout = html.Div([
    html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink('Pilots', href='/pilots')),
                dbc.NavItem(dbc.NavLink('Aircraft', href='/aircrafts')),
                dbc.NavItem(dbc.NavLink('School', href='/school')),
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
    dash.page_container
])




if __name__ == '__main__':
    # Run app
    app.run_server(debug=False)