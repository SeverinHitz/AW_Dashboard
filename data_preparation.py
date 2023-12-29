import os
import pandas as pd

# Disable the SettingWithCopyWarning
pd.options.mode.chained_assignment = None

def load_data():
    # Set directory
    program_path = os.path.realpath(__file__)
    cwd = os.path.dirname(program_path)
    data_dir = os.path.join(cwd, 'data')

    # Import Data from Excel File
    # Set Paths
    flight_log_path = os.path.join(data_dir, '231228_flightlog.xlsx')
    instructor_log_path = os.path.join(data_dir, '231228_instructorlog.xlsx')

    fligth_df = pd.read_excel(flight_log_path)
    instructor_df = pd.read_excel(instructor_log_path)

    return fligth_df, instructor_df


def data_cleanup(df, data_type):
    if data_type == 'flightlog':
        df = data_cleanup_flightlog(df)
    elif data_type == 'instructorlog':
        df = data_cleanup_instructorlog(df)
    else:
        raise 'Incorrect Datatype. Must be flightlog or instructorlog.'
        df = None
    return df

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
    )
    agg_df['Total_Flight_Time'] = agg_df['Total_Flight_Time'].dt.total_seconds() / 3600

    agg_df.sort_values('Total_Flight_Time', ascending=False, inplace=True)
    agg_df.reset_index(inplace=True)
    return agg_df

def date_aggregation(df, date_format):
    agg_df = df[['Date', 'YYYY', 'YY-MM', 'YY-MM-DD', 'Flight Time']]
    agg_df = agg_df.groupby(date_format).agg(
        Total_Flight_Time=pd.NamedAgg(column='Flight Time', aggfunc='sum')
    )
    agg_df['Total_Flight_Time'] = agg_df['Total_Flight_Time'].dt.total_seconds() / 3600
    return agg_df

if __name__ == '__main__':
    flight_df, instructor_df = load_data()

    flight_df = data_cleanup(flight_df, 'flightlog')
    instructor_df = data_cleanup(instructor_df, 'instructorlog')


    start_date = flight_df['Date'].min()
    end_date = flight_df['Date'].max()

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    agg_flight_df = pilot_aggregation(flight_df)
    agg_instructor_df = instructor_aggregation(instructor_df)



    date_flight_df = date_aggregation(flight_df, 'YYYY')




