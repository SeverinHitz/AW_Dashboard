import os
import pandas as pd
import geopandas as gpd
from datetime import datetime
from icecream import ic

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

    df.sort_values('Date', ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
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

    df.sort_values('Date', ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
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

    df.sort_values('First Name', ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)

    return df

def data_cleanup_reservation(df):
    # Select Columns
    df = df[['Von',
           'Bis',
           'Vorname',
           'Name',
           'Flugzeug',
           'Typ',
           'Gelöscht',
           'Löschgrund',
           'Geplante Flugzeit (hh:mm)']]

    new_column = {
        'Von': 'From',
        'Bis': 'To',
        'Vorname': 'First Name',
        'Name': 'Last Name',
        'Flugzeug': 'Airplane',
        'Typ': 'Type',
        'Gelöscht': 'Deleted',
        'Löschgrund': 'Deletion Reason',
        'Geplante Flugzeit (hh:mm)': 'Planned Flight Time'
    }
    df = df.rename(columns=new_column)
    # Pilot Full Name as Column
    df['Pilot'] = df['First Name'] + ' ' + df['Last Name']
    # Change Ja Nein to True False
    df['Deleted'] = df['Deleted'].map({'Ja': True, 'Nein': False})

    # Set Time as Timedelta
    df['Duration'] = df['To'] - df['From']
    df['Duration'] = pd.to_timedelta(df['Duration'].astype(str))

    # Simplify Deletion Reason
    # Define your lists
    weather = ['wetter', 'wx', 'wind', 'regen', 'böen', 'schnee', 'nebel', 'sturm', 'meteo', 'fog', 'bise',
               'turbulenzen', 'unsuitable', 'forecast', 'prognostiziert', 'conditions', 'cloud', 'stormy', 'ifr', 'imc',
               'snow', 'visibility', 'näfu']
    pax = ['passagier', 'pax', 'passenger', 'kunden', 'client', 'gäste', 'guest', 'fahrgast', 'fahrgäste', 'kunde']
    scheduling = ['termin', 'appointment', 'meeting', 'verpflichtung', 'commitment', 'geschäftstermin',
                  'business appointment', 'plan', 'schedule', 'verabredung', 'rendezvous', 'umplanung', 'reschedule',
                  'verschieben', 'terminkonflikt', 'planänderung']
    sickness = ['krank', 'ill', 'krankheit', 'sickness', 'unwell', 'gesundheitlich', 'health', 'erkrankt', 'illness',
                'nicht fit', 'unfit', 'covid', 'erkältet', 'fit', 'medical', 'sick']
    backup = ['backup', 'reserve', 'reserveflug']

    # Create a dictionary for categorization
    categories_dict = {
        'Weather': weather,
        'Pax': pax,
        'Scheduling': scheduling,
        'Sickness': sickness,
        'Backup': backup
    }

    # Create a function to categorize the reason (case-insensitive)
    def categorize_reason(reason):
        reason_lower = reason.lower()
        for category, words in categories_dict.items():
            if any(word in reason_lower for word in words):
                return category
        if reason_lower == 'nan':
            return 'None'
        if reason_lower:
            return 'Other'
        return None


    # Convert the 'Deletion Reason' column to lowercase after converting to string
    df['Deletion Reason'] = df['Deletion Reason'].astype(str).str.lower()

    # Replace NaN values with 'NaN' string for categorization
    df['Deletion Reason'] = df['Deletion Reason'].replace('nan', 'NaN')

    # Apply the categorization function to the 'Deletion Reason' column
    df['Deletion Reason'] = df['Deletion Reason'].apply(categorize_reason)

    # Set Time as Timedelta
    df['Duration'] = pd.to_timedelta(df['Duration'].astype(str))

    df.sort_values('From', ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)

    return df

def data_cleanup_gem_df(gdf):
    gdf = gdf[['PLZ', 'geometry']]

    return gdf

def date_select_df(df, start_date, end_date, date_column='Date'):
    df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
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

    # Calculate age at joining
    df['Age at Joining'] = df['Age'] - (current_year - df['Joining Year'])

    return df

def reservation_aggregation(df):
    # Create a new column 'Accepted' based on the condition
    df['Accepted'] = df.apply(lambda row: row['Duration'] if not row['Deleted'] else pd.Timedelta(0), axis=1)

    agg_df = df.groupby('Pilot').agg(
        Total_Reservation_Duration=pd.NamedAgg(column='Duration', aggfunc='sum'),
        Reservations=pd.NamedAgg(column='Duration', aggfunc='count'),
        Cancelled=pd.NamedAgg(column='Deleted', aggfunc='sum'),
        Accepted_Reservation_Duration=pd.NamedAgg(column='Accepted', aggfunc='sum')
    )
    agg_df['Ratio_Cancelled'] = agg_df['Cancelled'] / agg_df['Reservations']
    agg_df['Total_Reservation_Duration'] = agg_df['Total_Reservation_Duration'].dt.total_seconds() / 3600
    agg_df['Accepted_Reservation_Duration'] = agg_df['Accepted_Reservation_Duration'].dt.total_seconds() / 3600

    agg_df.sort_values('Total_Reservation_Duration', ascending=False, inplace=True)
    agg_df.reset_index(inplace=True)
    return agg_df

def reservation_flight_merge(agg_res_df, agg_pilot_df, sort_column='Accepted_Reservation_Duration'):

    agg_pilot_df = agg_pilot_df[['Pilot', 'Total_Flight_Time', 'Number_of_Flights']]

    merged_df = agg_res_df.merge(agg_pilot_df, on='Pilot', how='inner')

    merged_df['Flight_to_Reservation_Time'] = merged_df['Total_Flight_Time'] / merged_df['Accepted_Reservation_Duration']
    merged_df['Flight_per_Reservation'] = merged_df['Number_of_Flights'] / merged_df[
        'Accepted_Reservation_Duration']

    merged_df.sort_values(sort_column, ascending=False, inplace=True)
    merged_df.reset_index(inplace=True, drop=True)
    return merged_df


if __name__ == '__main__':
    flightlog_file = '240113_flightlog.xlsx'
    instructorlog_file = '240113_instructorlog.xlsx'
    member_path = '231230_members.xlsx'
    reservationlog_file = '240113_reservationlog.xlsx'

    # Import Dataframes
    flight_df = load_data(flightlog_file)
    instructor_df = load_data(instructorlog_file)
    member_df = load_data(member_path)
    reservation_df = load_data(reservationlog_file)

    flight_df = data_cleanup_flightlog(flight_df)
    instructor_df = data_cleanup_instructorlog(instructor_df)
    member_df = data_cleanup_member(member_df)
    reservation_df = data_cleanup_reservation(reservation_df)
    ic(reservation_df[reservation_df['Deleted']]['Deletion Reason'].value_counts())


    start_date = flight_df['Date'].min()
    end_date = flight_df['Date'].max()

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    agg_flight_df = pilot_aggregation(flight_df)
    agg_instructor_df = instructor_aggregation(instructor_df)







