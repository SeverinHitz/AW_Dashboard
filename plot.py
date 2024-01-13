import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
import pandas as pd

import data_preparation as dp

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

def member_histogram(df, template, color_discrete_sequence, margin, paper_bgcolor):

    # Create the bar chart with a color scale
    fig = px.histogram(
        df,
        x='Age',
        template=template,
        color_discrete_sequence=color_discrete_sequence
    )
    fig.update_layout(margin=margin,
                      paper_bgcolor=paper_bgcolor)

    return fig

def memeber_join_linegraph(df, template, color_discrete_sequence, margin, paper_bgcolor):
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
                   line=dict(color=color_discrete_sequence[0])),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=plot_df.index,
                   y=plot_df['Number of New Members'],
                   mode="lines",
                   name="# New Members",
                   line=dict(color=color_discrete_sequence[5])),
        secondary_y=True,
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Mean Age", secondary_y=False)
    fig.update_yaxes(title_text="Number of New Members", secondary_y=True)

    # Set the template to 'plotly_dark'
    fig.update_layout(template=template)
    fig.update_layout(margin=margin,
                      paper_bgcolor=paper_bgcolor)

    return fig

def member_location_graph(df, gdf, template, color_continuous_scale, margin, paper_bgcolor):
    df = df.groupby('PLZ').size().reset_index(name='count')
    # Merge 'agg_mem_df' with 'gem_gdf' while preserving the 'count' column
    df = pd.merge(df, gdf, on='PLZ')
    # Create a GeoDataFrame from the merged DataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry')

    gdf.set_index('PLZ', inplace=True)

    fig = px.choropleth_mapbox(gdf,
                               geojson=gdf.geometry,
                               locations=gdf.index,
                               color='count',
                               color_continuous_scale=color_continuous_scale,
                               opacity=0.8,
                               center={"lat": 47.23848, "lon": 8.51514},
                               mapbox_style='open-street-map',
                               zoom=8.5)

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=margin,
                      paper_bgcolor=paper_bgcolor)

    return fig

if __name__ == '__main__':
    flight_df, _ = dp.load_data()
    flight_df = dp.data_cleanup(flight_df, 'flightlog')
    fig = sankey_diagram(flight_df)
    fig.show()