# Settings for all Files like Layout, Stylesheet, Plot layout, colors
import dash_bootstrap_components as dbc
def init():
    # Stylsheet for General Look out of Bootstrap:
    # https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/
    global stylesheet
    stylesheet = dbc.themes.SLATE #YETI

    # Layoutcolor for general look, works with the Stylesheet
    global layout_color
    layout_color = 'dark' #None

    # Template for general Look of Plots from Plotly
    global plot_template
    plot_template = 'plotly_dark' #'plotly_white'

    # Color Continuous Scale for Plots
    global color_scale
    color_scale = 'teal'

    # Plot Margin for Border around Plots
    global plot_margin
    plot_margin = dict(l=5, r=5, t=5, b=5)

    # Transparent Background for Plots
    global paper_bgcolor
    paper_bgcolor = 'rgba(0,0,0,0)'

    # Border Around Plotwindow for smooth edges
    global plot_window_style
    plot_window_style = { 'border-radius':'5px', 'background-color':'None'}

    # Discrete Colors for Plots based on manual picking from Continuous Color scale
    global discrete_teal
    discrete_teal = ['#2c5977', '#3a718d', '#4f90a6', '#62a5b4', '#7dbdc4', '#8fcacd', '#a1d7d6', '#E4FFFF', '#cfede9']

    # Grid Color for Plots
    global grid_color
    grid_color = 'lightgrey'

    # Parameter for Legend of Plots
    global legend
    legend = dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor='rgba(255, 255, 255, 0.2)')