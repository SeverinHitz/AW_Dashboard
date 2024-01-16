# Analytics page

# Libraries
from icecream import ic
import dash
from dash import html

dash.register_page(__name__, path='/analytics', name='Analytics')

layout = html.Div([
    html.H2('Analytics Page')
])