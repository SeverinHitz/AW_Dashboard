# Aircrafts page

# Libraries
from icecream import ic
import dash
from dash import html

dash.register_page(__name__, path='/aircrafts', name='Aircrafts')

layout = html.Div([
    html.H2('Aircrafts Page')
])