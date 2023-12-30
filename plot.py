import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import data_preparation as dp

def sankey_diagram(df):
    # Select Columns
    df = df[['Departure Location', 'Arrival Location']]
    # distinguish between from and to
    # Aggregate Flights
    agg_df = df.groupby(['Departure Location', 'Arrival Location']).size().reset_index(name='Count')
    agg_df.columns = ['Departure Location', 'Arrival Location', 'Count']
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
        if item == 'LSZN':
            label_colors.append('yellow')
        elif item.startswith('LS'):
            label_colors.append('red')
        else:
            label_colors.append('grey')
    def assign_color(row):
        if row['Departure Location'] == 'LSZN' and row['Arrival Location'] == 'LSZN':
            return 'rgba(255, 255, 0, 0.5)'  # Yellow with alpha 0.5
        elif row['Departure Location'].startswith('LS') and row['Arrival Location'].startswith('LS'):
            return 'rgba(255, 0, 0, 0.5)'  # Red with alpha 0.5
        elif row['Departure Location'].startswith('LS') or row['Arrival Location'].startswith('LS'):
            return 'rgba(255, 0, 0, 0.25)'  # Red with alpha 0.25
        else:
            return 'rgba(128, 128, 128, 0.25)'  # Grey with alpha 0.25


    # Apply the function to create the new 'Color' column
    agg_df['Color'] = df.apply(assign_color, axis=1)


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

    fig.update_layout(title_text="Flight Route Sankey Diagram", font_size=10)

    return fig


if __name__ == '__main__':
    flight_df, _ = dp.load_data()
    flight_df = dp.data_cleanup(flight_df, 'flightlog')
    fig = sankey_diagram(flight_df)
    fig.show()