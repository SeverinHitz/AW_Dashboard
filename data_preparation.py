import os
import pandas as pd
import geopandas as gpd
from datetime import datetime

# Disable the SettingWithCopyWarning
pd.options.mode.chained_assignment = None

def load_data(path):
    # Set directory
    program_path = os.path.realpath(__file__)
    cwd = os.path.dirname(program_path)
    data_dir = os.path.join(cwd, 'data')

    # Import Data from Excel File
    # Set Paths
    path = os.path.join(data_dir, path)
    df = pd.read_excel(path)

    return df

def load_geodata(path):
    # Set directory
    program_path = os.path.realpath(__file__)
    cwd = os.path.dirname(program_path)
    data_dir = os.path.join(cwd, 'data')

    # Import Data from Excel File
    # Set Paths
    path = os.path.join(data_dir, path)
    # Daten einlesen
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(epsg=4326)

    return gdf

def data_cleanup_flightlog(df):
    # Select Columns
    df = df[['Datum', 'Vorname', 'Name', 'Abflugort', 'Ankunftsort',\
        'FlugzeitFlugzeit', 'Block Zeit', 'Benzin', 'Öl', 'Landungen',\
        'Flugart', 'Flugzeug']]

    # Rename Columns
    column_mapping = {
        'Datum': 'Date',
        'Vorname': 'First Name',
        'Name': 'Last Name',
        'Abflugort': 'Departure Location',
        'Ankunftsort': 'Arrival Location',
        'FlugzeitFlugzeit': 'Flight Time',
        'Block Zeit': 'Block Time',
        'Benzin': 'Fuel',
        'Öl': 'Oil',
        'Landungen': 'Landings',
        'Flugart': 'Flight Type',
        'Flugzeug': 'Aircraft'
    }
    df.rename(columns=column_mapping, inplace=True)
    # Pilot Full Name as Column
    df['Pilot'] = df['First Name'] + ' ' + df['Last Name']

    df['YYYY'] = df['Date'].dt.strftime('%Y')
    df['YY-MM'] = df['Date'].dt.strftime('%y-%m')
    df['YY-MM-DD'] = df['Date'].dt.strftime('%y-%m-%d')

    # Set Time as Timedelta
    df['Flight Time'] = pd.to_timedelta(df['Flight Time'].astype(str))
    df['Block Time'] = pd.to_timedelta(df['Block Time'].astype(str))
    return df

def data_cleanup_instructorlog(df):
    # Select Columns
    df = df[['Datum', 'Pilot Vorname', 'Pilot Name', 'Fluglehrer Vorname', 'Fluglehrer Name',\
        'Dauer']]

    # Rename Columns
    column_mapping = {
        'Datum': 'Date',
        'Pilot Vorname': 'Pilot First Name',
        'Pilot Name': 'Pilot Last Name',
        'Fluglehrer Vorname': 'Instructor First Name',
        'Fluglehrer Name': 'Instructor Last Name',
        'Dauer': 'Duration'
    }
    df.rename(columns=column_mapping, inplace=True)

    # Pilot and Instructor Full Name as Column
    df['Pilot'] = df['Pilot First Name'] + ' ' + df['Pilot Last Name']
    df['Instructor'] = df['Instructor First Name'] + ' ' + df['Instructor Last Name']

    df['YYYY'] = df['Date'].dt.strftime('%Y')
    df['YY-MM'] = df['Date'].dt.strftime('%y-%m')
    df['YY-MM-DD'] = df['Date'].dt.strftime('%y-%m-%d')

    # Set Time as Timedelta
    df['Duration'] = pd.to_timedelta(df['Duration'].astype(str))
    return df

def data_cleanup_member(df):
    # Select Columns
    df = df[['AirManager ID', 'Vorname', 'Name', 'Strasse', 'PLZ', 'Ort', 'Land', 'Geburtsdatum', 'Mitgliedschaft',
          'Eintrittsdatum']]

    # Rename in English
    new_columns = {
        'AirManager ID': 'AirManager ID',
        'Vorname': 'First Name',
        'Name': 'Last Name',
        'Strasse': 'Street',
        'PLZ': 'PLZ',
        'Ort': 'City',
        'Land': 'Country',
        'Geburtsdatum': 'Date of Birth',
        'Mitgliedschaft': 'Membership',
        'Eintrittsdatum': 'Join Date'
    }

    df.rename(columns=new_columns, inplace=True)

    df = df[df['Membership'] == 'Aktiv']

    return df


def data_cleanup_gem_df(gdf):
    gdf = gdf[['PLZ', 'geometry']]

    return gdf

def date_select_df(df, start_date, end_date):
    df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    return df

def pilot_aggregation(df, sort_column='Total_Flight_Time'):
    agg_df = df.groupby('Pilot').agg(
        Total_Flight_Time=pd.NamedAgg(column='Flight Time', aggfunc='sum'),
        Total_Block_Time=pd.NamedAgg(column='Block Time', aggfunc='sum'),
        Number_of_Landings=pd.NamedAgg(column='Landings', aggfunc='sum'),
        Number_of_Different_Airports=pd.NamedAgg(column='Arrival Location', aggfunc=lambda x: x.nunique()),
        Number_of_Flights=pd.NamedAgg(column='Flight Time', aggfunc='count'),
    )
    agg_df['Total_Flight_Time'] = agg_df['Total_Flight_Time'].dt.total_seconds() / 3600
    agg_df['Total_Block_Time'] = agg_df['Total_Block_Time'].dt.total_seconds() / 3600

    agg_df.sort_values(sort_column, ascending=False, inplace=True)
    agg_df.reset_index(inplace=True)
    return agg_df

def instructor_aggregation(df, sort_column='Total_Duration'):
    agg_df = df.groupby('Instructor').agg(
        Total_Duration=pd.NamedAgg(column='Duration', aggfunc='sum'),
        Number_of_Different_Pilots=pd.NamedAgg(column='Pilot', aggfunc=lambda x: x.nunique()),
        Number_of_Instructions=pd.NamedAgg(column='Duration', aggfunc='count'),
    )
    agg_df['Total_Duration'] = agg_df['Total_Duration'].dt.total_seconds() / 3600
    agg_df.sort_values(sort_column, ascending=False, inplace=True)
    agg_df.reset_index(inplace=True)
    return agg_df

def aircraft_aggregation(df):
    agg_df = df.groupby('Aircraft').agg(
        Total_Flight_Time=pd.NamedAgg(column='Flight Time', aggfunc='sum'),
        Number_of_Landings=pd.NamedAgg(column='Landings', aggfunc='sum'),
        Number_of_Different_Airports=pd.NamedAgg(column='Arrival Location', aggfunc=lambda x: x.nunique()),
        Number_of_Flights=pd.NamedAgg(column='Flight Time', aggfunc='count'),
        Total_Fuel=pd.NamedAgg(column='Fuel', aggfunc='sum'),
        Total_Oil=pd.NamedAgg(column='Oil', aggfunc='sum'),
    )
    agg_df['Total_Flight_Time'] = agg_df['Total_Flight_Time'].dt.total_seconds() / 3600

    agg_df['Fuel_per_hour'] = agg_df['Total_Fuel'] / agg_df['Total_Flight_Time']
    agg_df['Oil_per_hour'] = agg_df['Total_Oil'] / agg_df['Total_Flight_Time']

    round_cols_1 = ['Total_Flight_Time', 'Total_Fuel', 'Fuel_per_hour']
    agg_df[round_cols_1] = agg_df[round_cols_1].round(1)
    round_cols_3 = ['Total_Oil', 'Oil_per_hour']
    agg_df[round_cols_3] = agg_df[round_cols_3].round(3)

    agg_df.sort_values('Total_Flight_Time', ascending=False, inplace=True)
    agg_df.reset_index(inplace=True)
    return agg_df

def date_aggregation(df, date_format, agg_column):
    agg_df = df[['Date', 'YYYY', 'YY-MM', 'YY-MM-DD', agg_column]]
    agg_df = agg_df.groupby(date_format).agg(
        Total_Time=pd.NamedAgg(column=agg_column, aggfunc='sum')
    )
    agg_df['Total_Time'] = agg_df['Total_Time'].dt.total_seconds() / 3600
    agg_df.reset_index(inplace=True)
    return agg_df

def member_aggregation(df):
    current_year = datetime.now().year
    df['Age'] = pd.to_datetime(df['Date of Birth'], errors='coerce').apply(
        lambda x: current_year - x.year if pd.notnull(x) else np.nan)
    df['Joining Year'] = pd.to_datetime(df['Join Date'], errors='coerce').dt.year
    # Drop rows where age or joining year is NaN
    df = df.dropna(subset=['Age', 'Joining Year'])

    return df

if __name__ == '__main__':
    flightlog_file = '231228_flightlog.xlsx'
    instructorlog_file = '231228_instructorlog.xlsx'
    member_path = '231230_members.xlsx'

    # Import Dataframes
    flight_df = load_data(flightlog_file)
    instructor_df = load_data(instructorlog_file)
    member_df = load_data(member_path)

    flight_df = data_cleanup_flightlog(flight_df)
    instructor_df = data_cleanup_instructorlog(instructor_df)
    member_df = data_cleanup_member(member_df)
    member_df = member_aggregation(member_df)
    print(list(member_df))

    # Geographical data
    # Path
    gemeinde_path = 'PLZO_PLZ.shp'
    # Import
    gem_gdf = load_geodata(gemeinde_path)
    # Cleanup
    gem_gdf = data_cleanup_gem_df(gem_gdf)
    print(gem_gdf)

    start_date = flight_df['Date'].min()
    end_date = flight_df['Date'].max()

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    agg_flight_df = pilot_aggregation(flight_df)
    agg_instructor_df = instructor_aggregation(instructor_df)







