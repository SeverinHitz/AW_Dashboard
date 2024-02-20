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

    # Plot Margin for maps
    global plot_margin_map
    plot_margin_map = dict(l=0, r=0, t=0, b=0)

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
    legend = dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor='rgba(255, 255, 255, 0.4)')

    global adaptiv_width_1
    adaptiv_width_1 = {'xs':12, 'sm':6, 'md':3, 'lg':2, 'xl':1}

    global adaptiv_width_2
    adaptiv_width_2 = {'xs':12, 'sm':6, 'md':3, 'lg':2, 'xl':2}

    global adaptiv_width_3
    adaptiv_width_3 = {'xs':12, 'sm':6, 'md':3, 'lg':3, 'xl':3}

    global adaptiv_width_4
    adaptiv_width_4 = {'xs':12, 'sm':6, 'md':6, 'lg':4, 'xl':4}

    global adaptiv_width_5
    adaptiv_width_5 = {'xs':12, 'sm':12, 'md':5, 'lg':5, 'xl':5}

    global adaptiv_width_6
    adaptiv_width_6 = {'xs':12, 'sm':12, 'md':6, 'lg':6, 'xl':6}

    global adaptiv_width_7
    adaptiv_width_7 = {'xs':12, 'sm':12, 'md':12, 'lg':7, 'xl':7}

    global adaptiv_width_8
    adaptiv_width_8 = {'xs':12, 'sm':12, 'md':12, 'lg':8, 'xl':8}

    global adaptiv_width_12
    adaptiv_width_12 = {'xs':12, 'sm':12, 'md':12, 'lg':12, 'xl':12}

