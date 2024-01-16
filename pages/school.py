# School page

# Libraries
from icecream import ic
import dash
from dash import html

dash.register_page(__name__, path='/school', name='School')

layout = html.Div([
    html.H2('School Page')
])