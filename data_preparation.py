import os
import pandas as pd
import geopandas as gpd
from datetime import datetime
from icecream import ic
from shapely.geometry import Point
import numpy as np

# Disable the SettingWithCopyWarning
pd.options.mode.chained_assignment = None

# -------------------------------------------- Load Data ----------------------------------------------------------#

def load_data(filename):
    # Set directory
    program_path = os.path.realpath(__file__)
    cwd = os.path.dirname(program_path)
    data_dir = os.path.join(cwd, 'data')

    # Get file extension
    file_extension = filename.split('.')[-1].lower()

    # Import data based on file extension
    path = os.path.join(data_dir, filename)
    if file_extension == 'csv':
        df = pd.read_csv(path)
    elif file_extension in ['xls', 'xlsx']:
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported file format. Only CSV, XLS, or XLSX are supported.")

    return df


def load_geodata(filename, convert_crs=True):
    # Set directory
    program_path = os.path.realpath(__file__)
    cwd = os.path.dirname(program_path)
    data_dir = os.path.join(cwd, 'data')

    # Import Data from Excel File
    # Set Paths
    path = os.path.join(data_dir, filename)
    # Daten einlesen
    gdf = gpd.read_file(path)
    if convert_crs:
        gdf = gdf.to_crs(epsg=4326)

    return gdf


def load_eu_airports(filename):
    # Assuming load_geodata returns a DataFrame with 'latitude_deg' and 'longitude_deg' columns
    eu_airports_df = load_data(filename)

    # Convert latitude and longitude to float
    eu_airports_df['latitude_deg'] = eu_airports_df['latitude_deg'].astype(float)
    eu_airports_df['longitude_deg'] = eu_airports_df['longitude_deg'].astype(float)

    # Create a new DataFrame with 'name', 'ident', 'latitude', and 'longitude' columns
    eu_airports_df = eu_airports_df[['name', 'ident', 'latitude_deg', 'longitude_deg']]

    # adding the glacier LSZZ with Aletschgletscher Position as a new row
    new_entry = {'name': 'Glacier', 'ident': 'LSZZ', 'latitude_deg': 46.50543, 'longitude_deg': 8.03335}
    eu_airports_df = pd.concat([eu_airports_df, pd.DataFrame([new_entry])], ignore_index=True)

    return eu_airports_df


def reload_flightlog_dataframe_from_dict(dict, start_date, end_date, offset=0):
    # Load Data from Store
    flight_df = pd.DataFrame.from_dict(dict)
    # Convert the 'date_column' to timestamps
    flight_df['Date'] = pd.to_datetime(flight_df['Date'])
    # Set Time as Timedelta
    flight_df['Flight Time'] = pd.to_timedelta(flight_df['Flight Time'].astype(str))
    flight_df['Block Time'] = pd.to_timedelta(flight_df['Block Time'].astype(str))
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if offset != 0:
        # Subtract one year from start_date and end_date
        start_date -= pd.DateOffset(years=offset)
        end_date -= pd.DateOffset(years=offset)

    # Filter Flightlog data based on the selected date range
    filtered_flight_df = date_select_df(flight_df, start_date, end_date)

    return filtered_flight_df

def reload_instructor_dataframe_from_dict(dict, start_date, end_date, offset=0):
    # Load Data from Store
    instructor_df = pd.DataFrame.from_dict(dict)
    # Convert the 'date_column' to timestamps
    instructor_df['Date'] = pd.to_datetime(instructor_df['Date'])
    # Set Time as Timedelta
    instructor_df['Duration'] = pd.to_timedelta(instructor_df['Duration'].astype(str))
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if offset != 0:
        # Subtract one year from start_date and end_date
        start_date -= pd.DateOffset(years=offset)
        end_date -= pd.DateOffset(years=offset)

    # Filter Instructorlog data based on the selected date range
    filtered_instructor_df = date_select_df(instructor_df, start_date, end_date)

    return filtered_instructor_df

def reload_reservation_dataframe_from_dict(dict, start_date, end_date):
    # Load Data from Store
    reservation_df = pd.DataFrame.from_dict(dict)
    # Set Time as Timedelta
    reservation_df['Duration'] = pd.to_timedelta(reservation_df['Duration'].astype(str))
    # Convert the 'date_column' to timestamps
    reservation_df['From'] = pd.to_datetime(reservation_df['From'])
    # Set Date as a Datetime object
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter Instructorlog data based on the selected date range
    filtered_reservation_df = date_select_df(reservation_df, start_date, end_date, date_column='From')

    return filtered_reservation_df

def reload_member_dataframe_from_dict(dict):
    # Load Data from Store
    member_df = pd.DataFrame.from_dict(dict)

    # Convert the 'date_column' to timestamps
    member_df['Date of Birth'] = pd.to_datetime(member_df['Date of Birth'])

    return member_df


#----------------------------------------------- Clean up Data ----------------------------------------------------#

def xls_format_cleanup(df):
    # Date Columns
    date_columns_1 = ['Datum', 'Geburtsdatum']  # Format = dd.mm.yyyy
    date_columns_2 = ['Eintrittsdatum'] # Format = yyyy-mm-dd

    # Time Delta Columns
    timedelta_columns = ['Dauer'] # Format = hh:mm

    # Datetime Colums
    datetime_columns = ['Von', 'Bis'] # Format = dd.mm.yyyy hh:mm:ss

    for col in date_columns_1:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%d.%m.%Y', errors='coerce')

    for col in date_columns_2:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%Y-%m-%d', errors='coerce')

    for col in timedelta_columns:
        if col in df.columns:
            df[col] = pd.to_timedelta(df[col].astype(str) + ':00')

    for col in datetime_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%d.%m.%Y %H:%M:%S', errors='coerce')

    # Problem with Merge on integer
    integer_columns = ['PLZ']

    for col in integer_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

def data_cleanup_flightlog(df):
    # Select Columns
    df = df[['Datum', 'Vorname', 'Name', 'Abflugort', 'Ankunftsort',\
        'Flugzeit', 'Block Zeit', 'Benzin', 'Öl', 'Landungen',\
        'Flugart', 'Flugzeug']]

    # Rename Columns
    column_mapping = {
        'Datum': 'Date',
        'Vorname': 'First Name',
        'Name': 'Last Name',
        'Abflugort': 'Departure Location',
        'Ankunftsort': 'Arrival Location',
        'Flugzeit': 'Flight Time',
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
    df['YY-WW'] = df['Date'].dt.strftime('%y-%W')

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
    df['YY-WW'] = df['Date'].dt.strftime('%y-%W')

    # Set Time as Timedelta
    df['Duration'] = pd.to_timedelta(df['Duration'].astype(str))

    df.sort_values('Date', ascending=False, inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df

def data_cleanup_member(df):
    # Select Columns
    df = df[['AirManager ID', 'PLZ', 'Geburtsdatum', 'Mitgliedschaft',
          'Eintrittsdatum']]

    # Rename in English
    new_columns = {
        'AirManager ID': 'AirManager ID',
        'PLZ': 'PLZ',
        'Land': 'Country',
        'Geburtsdatum': 'Date of Birth',
        'Mitgliedschaft': 'Membership',
        'Eintrittsdatum': 'Join Date'
    }

    df.rename(columns=new_columns, inplace=True)
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
           'Löschgrund']]

    new_column = {
        'Von': 'From',
        'Bis': 'To',
        'Vorname': 'First Name',
        'Name': 'Last Name',
        'Flugzeug': 'Airplane',
        'Typ': 'Type',
        'Gelöscht': 'Deleted',
        'Löschgrund': 'Deletion Reason'
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
    weather = ['wetter', 'weather', 'wx', 'wind', 'regen', 'böen', 'schnee', 'nebel', 'sturm', 'meteo', 'fog', 'bise',
               'turbulenzen', 'unsuitable', 'forecast', 'prognostiziert', 'conditions', 'cloud', 'stormy', 'ifr', 'imc',
               'snow', 'visibility', 'näfu', 'gewitter', 'met', 'icy', 'icing']
    pax = ['passagier', 'pax', 'passenger', 'kunden', 'client', 'gäste', 'guest', 'fahrgast', 'fahrgäste', 'kunde']
    scheduling = ['termin', 'appointment', 'meeting', 'verpflichtung', 'commitment', 'geschäftstermin',
                  'business appointment', 'plan', 'schedule', 'verabredung', 'rendezvous', 'umplanung', 'reschedule',
                  'verschieben', 'terminkonflikt', 'planänderung', 'unfall']
    sickness = ['krank', 'ill', 'krankheit', 'sickness', 'unwell', 'gesundheitlich', 'health', 'erkrankt', 'illness',
                'nicht fit', 'unfit', 'covid', 'erkältet', 'fit', 'medical', 'sick', 'gesundheit']
    backup = ['backup', 'reserve', 'reserveflug', 'back up']
    maintenance = ['maintenance', 'werkstatt', 'acft', 'flugzeugwechsel', 'reparatur', 'blockiert']
    fi = ['fi', 'fluglehrer', 'instructor']
    airport = ['airport', 'flugplatz', 'flugtag', 'modellflugtag', 'lszn', 'ad']
    wrong = ['falsch', 'fehler', 'test', 'duplicate', 'doppelt', 'doppelbuchung', 'umgebucht']

    # Create a dictionary for categorization
    categories_dict = {
        'Weather': weather,
        'Pax': pax,
        'Scheduling': scheduling,
        'Sickness': sickness,
        'Backup': backup,
        'Maintenance': maintenance,
        'FI N/A': fi,
        'Airport N/A': airport,
        'Wrong/Test': wrong
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

def data_diff_visual_bins(start_date, end_date):
    # Calculate the date offset between start_date and end_date
    date_offset = end_date - start_date

    # Define Timedeltas for comparison (in months)
    six_months_timedelta = pd.Timedelta(days=6 * 30.44)  # Approximately 6 months
    twelve_months_timedelta = pd.Timedelta(days=12 * 30.44)  # Approximately 12 months

    # Check the range using if statements
    if date_offset <= six_months_timedelta:
        col = 'Date'
    elif date_offset <= twelve_months_timedelta:
        col = 'YY-WW'
    else:
        col = 'YY-MM'

    return col

#-------------------------------------- Aggregate Data -----------------------------------------------------------#

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

    agg_df['Flight_Block_Ratio'] = agg_df['Total_Flight_Time'] / agg_df['Total_Block_Time']

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

def trainee_aggregation(df, sort_column='Total_Duration'):
    agg_df = df.groupby('Pilot').agg(
        Total_Duration=pd.NamedAgg(column='Duration', aggfunc='sum'),
        Number_of_Different_Instructors=pd.NamedAgg(column='Instructor', aggfunc=lambda x: x.nunique()),
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
        Number_of_Pilots=pd.NamedAgg(column='Pilot', aggfunc=lambda x: x.nunique()),
        Number_of_Instruction_Flights=pd.NamedAgg(column='Flight Type', aggfunc=lambda x: (x == 'Schulung VFR').sum())
    )
    agg_df['Total_Flight_Time'] = agg_df['Total_Flight_Time'].dt.total_seconds() / 3600

    agg_df['Fuel_per_hour'] = agg_df['Total_Fuel'] / agg_df['Total_Flight_Time']
    agg_df['Oil_per_hour'] = agg_df['Total_Oil'] / agg_df['Total_Flight_Time']
    agg_df['Mean_Flight_Time'] = agg_df['Total_Flight_Time']/agg_df['Number_of_Flights']
    agg_df['Instruction_Ratio'] = agg_df['Number_of_Instruction_Flights'] / agg_df['Number_of_Flights']

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
    df['Join Date'] = pd.to_datetime(df['Join Date'], errors='coerce')
    df['Joining Year'] = df['Join Date'].dt.year
    # Drop rows where age or joining year is NaN
    df = df.dropna(subset=['Age'])
    # Calculate age at joining
    df['Age at Joining'] = df['Age'] - (current_year - df['Joining Year'])
    return df

def reservation_aggregation(df):
    # Create a new column 'Accepted' based on the condition
    df['Accepted_Duration'] = df.apply(lambda row: row['Duration'] if not row['Deleted'] else pd.Timedelta(0), axis=1)

    agg_df = df.groupby('Pilot').agg(
        Total_Reservation_Duration=pd.NamedAgg(column='Duration', aggfunc='sum'),
        Reservations=pd.NamedAgg(column='Duration', aggfunc='count'),
        Cancelled=pd.NamedAgg(column='Deleted', aggfunc='sum'),
        Accepted_Reservation_Duration=pd.NamedAgg(column='Accepted_Duration', aggfunc='sum')
    )
    agg_df['Accepted'] = agg_df['Reservations'] - agg_df['Cancelled']
    agg_df['Ratio_Cancelled'] = agg_df['Cancelled'] / agg_df['Reservations']
    agg_df['Total_Reservation_Duration'] = agg_df['Total_Reservation_Duration'].dt.total_seconds() / 3600
    agg_df['Accepted_Reservation_Duration'] = agg_df['Accepted_Reservation_Duration'].dt.total_seconds() / 3600

    agg_df.sort_values('Total_Reservation_Duration', ascending=False, inplace=True)
    agg_df.reset_index(inplace=True)
    return agg_df

def heatmap_preparation(df, start_date, end_date, agg_column, date_column = 'Date'):
    # Datum in Kalenderwoche und Wochentag umwandeln, Jahr hinzufügen
    df['YearWeek'] = df[date_column].dt.strftime('%Y-W%V')
    df['Day'] = df[date_column].dt.dayofweek

    # Aktivität pro Kalenderwoche und Jahr aggregieren
    agg_df = df.groupby(['YearWeek', 'Day'])[agg_column].sum().reset_index()

    # Vollständigen Datumsbereich erstellen
    date_range = pd.date_range(start=start_date, end=end_date)
    full_df = pd.DataFrame(date_range, columns=[date_column])
    full_df['YearWeek'] = full_df[date_column].dt.strftime('%Y-W%V')
    full_df['Day'] = full_df[date_column].dt.dayofweek

    # Einzigartige Kombinationen von YearWeek und Day erstellen
    full_combinations = full_df[['YearWeek', 'Day']].drop_duplicates()

    # Stellen Sie sicher, dass alle Kombinationen im agg_df vorhanden sind
    agg_df = pd.merge(full_combinations, agg_df, on=['YearWeek', 'Day'], how='left').fillna(0)


    # Pivot-Tabelle für Heatmap vorbereiten
    pivot_df = agg_df.pivot(index="Day", columns="YearWeek", values=agg_column)

    pivot_df = pivot_df.map(lambda x: x.total_seconds() / 3600 if hasattr(x, 'total_seconds') else x)


    return pivot_df


#------------------------------------------ Merge Data ----------------------------------------------------------#
def reservation_flight_merge(agg_res_df, agg_pilot_df, sort_column='Accepted_Reservation_Duration'):

    merged_df = agg_res_df.merge(agg_pilot_df, on='Pilot', how='inner')

    merged_df['Flight_to_Reservation_Time'] = merged_df['Total_Flight_Time'] / merged_df['Accepted_Reservation_Duration']
    merged_df['Flight_per_Reservation'] = merged_df['Number_of_Flights'] / merged_df[
        'Accepted']

    merged_df.sort_values(sort_column, ascending=False, inplace=True)
    merged_df.reset_index(inplace=True, drop=True)
    return merged_df

#---------------------------------------------- Site Specific Functions ---------------------------------------------#

#---------------------------------------------- Main Page

def sum_time_per_Column(df, select_column, sum_column, acf=None):
    if select_column:
        sum_flight_time = df[df[select_column] == acf][sum_column].sum()
    else:
        sum_flight_time = df[sum_column].sum()
    total_minutes = sum_flight_time.total_seconds() // 60
    hours = total_minutes // 60
    minutes = total_minutes % 60
    formatted_time = f'{int(hours):02d}:{int(minutes):02d}'
    sum_flight_time_str = f'{formatted_time}h'
    return sum_flight_time_str


def agg_by_Day(df, date_column, group_column, agg_column, out_column):
    # Aggregate flight time for each aircraft on each date
    agg_df = df.groupby([group_column, date_column]).agg(
        sum=pd.NamedAgg(column=agg_column, aggfunc='sum'))
    agg_df = agg_df.rename(columns={'sum': out_column})
    # Reset the index to have a flat DataFrame
    agg_df.reset_index(inplace=True)

    # Convert the date_column column to datetime
    agg_df[date_column] = pd.to_datetime(agg_df[date_column])

    # Define the date range you're interested in
    date_range = pd.date_range(start=min(agg_df[date_column]), end=max(agg_df[date_column]))

    # Create a MultiIndex DataFrame with every date and aircraft combination
    multi_index = pd.MultiIndex.from_product([date_range, agg_df[group_column].unique()], names=[date_column, group_column])
    complete_df = pd.DataFrame(index=multi_index)

    # Merge the aggregated DataFrame with the complete DataFrame and fill NaN values with 0
    merged_df = complete_df.merge(agg_df, left_index=True, right_on=[date_column, group_column], how='left').fillna(
        {out_column: 0})

    merged_df[out_column] = pd.to_timedelta(merged_df[out_column].astype(str))

    merged_df[out_column] = merged_df[out_column].dt.total_seconds() / 3600

    return merged_df

#---------------------------------------Aircraft Page

def destination_aggregation(df, airports_df):
    agg_df = df.groupby('Arrival Location').agg(
        Total_Landings=pd.NamedAgg(column='Landings', aggfunc='sum')
    )
    agg_df.reset_index(inplace=True)
    agg_df.rename(columns={'Arrival Location': 'ident'}, inplace=True)
    merged_gdf = airports_df.merge(agg_df, on='ident', how='inner')
    merged_gdf['log_Total_Landings'] = np.log(merged_gdf['Total_Landings'])


    return merged_gdf






if __name__ == '__main__':

    eu_airports_file = 'eu-airports.csv'
    eu_airport_gdf = load_eu_airports(eu_airports_file)
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


    start_date = flight_df['Date'].min()
    end_date = flight_df['Date'].max()

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    arrival_count = destination_aggregation(flight_df, eu_airport_gdf)
    ic(arrival_count.columns)







