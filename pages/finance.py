# Finance page

# Libraries
from icecream import ic
import dash
from dash import html

dash.register_page(__name__, path='/finance', name='Finance')

layout = html.Div([
    html.H2('Finance Page')
])