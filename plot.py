# Library
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
import pandas as pd
from icecream import ic

import data_preparation as dp
import globals

globals.init()

def sankey_diagram(df, template):
    # Select Columns
    df = df[['Departure Location', 'Arrival Location']]
    df['Departure Location'] = 'From ' + df['Departure Location']
    df['Arrival Location'] = 'To ' + df['Arrival Location']
    # distinguish between from and to
    # Aggregate Flights
    agg_df = df.groupby(['Departure Location', 'Arrival Location']).size().reset_index(name='Count')
    agg_df.columns = ['Departure Location', 'Arrival Location', 'Count']
    agg_df.sort_values('Count', inplace=True)
    # Creating a mapping from location to integer index
    labels = set(df['Departure Location']).union(df['Arrival Location'])
    location_index_map = {location: index for index, location in
                          enumerate(labels)}
    # Adding new columns 'source' and 'target' with integer values
    agg_df['source'] = agg_df['Departure Location'].map(location_index_map)
    agg_df['target'] = agg_df['Arrival Location'].map(location_index_map)
    # Colors
    label_colors = []
    for item in labels:
        if 'LSZN' in item:
            label_colors.append('yellow')
        elif 'LS' in item:
            label_colors.append('red')
        else:
            label_colors.append('grey')
    def assign_color(row):
        if 'LSZN' in row['Departure Location'] and 'LSZN' in  row['Arrival Location']:
            return 'rgba(255, 255, 0, 0.5)'  # Yellow with alpha 0.5
        elif 'LS' in row['Departure Location'] and 'LS' in row['Arrival Location']:
            return 'rgba(255, 0, 0, 0.5)'  # Red with alpha 0.5
        elif 'LS' in row['Departure Location'] or 'LS' in row['Arrival Location']:
            return 'rgba(255, 0, 0, 0.25)'  # Red with alpha 0.25
        else:
            return 'rgba(128, 128, 128, 0.25)'  # Grey with alpha 0.25


    # Apply the function to create the new 'Color' column
    agg_df['Color'] = agg_df.apply(assign_color, axis=1)
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=list(labels),
            color=label_colors
        ),
        link=dict(
            source=agg_df['source'],
            target=agg_df['target'],
            value=agg_df['Count'],
            color=agg_df['Color']
        ))])

    fig.update_layout(title_text="Flight Route Sankey Diagram", font_size=10, template=template)
    fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))

    return fig

def member_histogram(df):

    # Create the bar chart with a color scale
    fig = px.histogram(
        df,
        x='Age',
        template=globals.plot_template,
        color_discrete_sequence=globals.discrete_teal
    )

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(margin=globals.plot_margin,
                      paper_bgcolor=globals.paper_bgcolor,
                      plot_bgcolor=globals.paper_bgcolor)

    return fig

def memeber_join_linegraph(df):
    # Calculate the mean age and number of new members for each year from 2015 to 2023
    plot_df = df.groupby('Joining Year').agg({'Age at Joining': 'mean', 'AirManager ID': 'count'}).loc[
                          2015:]

    # Rename the columns for clarity
    plot_df.columns = ['Mean Age', 'Number of New Members']

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=plot_df.index,
                   y=plot_df['Mean Age'],
                   mode="lines",
                   name="Mean Age",
                   line=dict(color=globals.discrete_teal[0]),
                   line_shape='spline'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=plot_df.index,
                   y=plot_df['Number of New Members'],
                   mode="lines",
                   name="# New Members",
                   line=dict(color=globals.discrete_teal[-1]),
                   line_shape='spline'),
        secondary_y=True,
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Mean Age", secondary_y=False)
    fig.update_yaxes(title_text="Number of New Members", secondary_y=True)

    # Synchronize the y-axes ranges
    fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey', secondary_y=False)
    fig.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey', secondary_y=True)

    # Set the template to 'plotly_dark'
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    fig.update_layout(template=globals.plot_template,
                      margin=globals.plot_margin,
                      paper_bgcolor=globals.paper_bgcolor,
                      plot_bgcolor=globals.paper_bgcolor,
                      legend=globals.legend)

    return fig

def member_location_graph(df, gdf):
    df = df.groupby('PLZ').size().reset_index(name='count')
    # Merge 'agg_mem_df' with 'gem_gdf' while preserving the 'count' column
    df = pd.merge(df, gdf, on='PLZ')
    # Create a GeoDataFrame from the merged DataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    # Make sure PLZ is an Integer. Because of Format Problems with direct airmanager export data
    gdf['PLZ'] = gdf['PLZ'].astype(int)

    gdf.set_index('PLZ', inplace=True)

    # Find the row(s) with the maximum 'count' value
    max_count = gdf['count'].max()
    max_count_row = gdf[gdf['count'] == max_count].iloc[0]

    # Calculate the centroid of the geometry in the selected row
    centroid_max = max_count_row.geometry.centroid

    fig = px.choropleth_mapbox(gdf,
                               geojson=gdf.geometry,
                               locations=gdf.index,
                               color='count',
                               color_continuous_scale=globals.color_scale,
                               opacity=0.8,
                               center={"lat": centroid_max.y, "lon": centroid_max.x},
                               mapbox_style='open-street-map',
                               zoom=8.5)

    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(margin=globals.plot_margin_map,
                      paper_bgcolor=globals.paper_bgcolor,
                      plot_bgcolor=globals.paper_bgcolor,
                      legend=globals.legend)

    return fig

def not_data_figure():
    # Use the plotly_dark template from Plotly's template collection
    not_data_template = go.layout.Template()

    not_data_template.layout.annotations = [
        dict(
            name="draft watermark",
            text="NO DATA",
            textangle=-30,
            opacity=0.5,
            font=dict(color="red", size=100),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
    ]

    fig = go.Figure()
    fig.update_layout(template=globals.plot_template)
    fig.update_layout(template=not_data_template)
    fig.update_layout(margin=globals.plot_margin,
                      paper_bgcolor=globals.paper_bgcolor,
                      plot_bgcolor=globals.paper_bgcolor,
                      legend=globals.legend)
    return fig


if __name__ == '__main__':
    flight_df, _ = dp.load_data()
    flight_df = dp.data_cleanup(flight_df, 'flightlog')
    fig = sankey_diagram(flight_df)
    fig.show()