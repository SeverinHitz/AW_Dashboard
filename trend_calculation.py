import os
import pandas as pd
import geopandas as gpd
from datetime import datetime
from icecream import ic
from shapely.geometry import Point
import numpy as np
import data_preparation as dp  # Custom module for data preparation tasks
import string_func as sf

def trend_calculation(selected, selected_t_minus):
    # Calculate Trend
    trend = []
    for i in range(len(selected)):
        trend.append((selected[i] / selected_t_minus[i] * 100) - 100)

    # Extract
    trend_strings, trend_styles = sf.trend_string(len(selected), trend)

    return trend_strings, trend_styles

# --------------------------------- Overview Page --------------------------------

# Flightlog
def select_overview_page_flightlog(df, df_trend):
    selected = sum_overview_page_flightlog(df) # Extract KPI specific Data
    selected_t_minus = sum_overview_page_flightlog(df_trend) # Extract KPI - one Year Data
    return selected, selected_t_minus

def sum_overview_page_flightlog(df):
    # Overview Page Flight Hours KPIs
    sum_flight_time = df['Flight Time'].sum()
    sum_flight_time = sum_flight_time.total_seconds() // 60
    # Sum of Flights
    sum_flight = len(df)
    sum_landings = df["Landings"].sum()
    sum_fuel = df["Fuel"].sum()

    return sum_flight_time, sum_flight, sum_landings, sum_fuel

# Instructor log
def select_overview_page_instructorlog(df, df_trend):
    selected = sum_overview_page_instructorlog(df)  # Extract KPI specific Data
    selected_t_minus = sum_overview_page_instructorlog(df_trend)  # Extract KPI - one Year Data

    return selected, selected_t_minus

def sum_overview_page_instructorlog(df):
    # Overview Page Flight Hours KPIs
    sum_instructor_hours = df['Duration'].sum()
    sum_instructor_hours = sum_instructor_hours.total_seconds() // 60
    # Sum of Flights
    sum_trainees = df['Pilot'].nunique()
    sum_instruction_sets = len(df)

    return sum_instructor_hours, sum_trainees, sum_instruction_sets

# -------------------------------- Pilot Page -------------------------------------------

def select_pilot_page_flightlog(df, df_trend, pilot_dropdown):
    selected = sum_pilot_page_flightlog(df, pilot_dropdown)  # Extract KPI specific Data
    selected_t_minus = sum_pilot_page_flightlog(df_trend, pilot_dropdown)  # Extract KPI - one Year Data

    return selected, selected_t_minus

def sum_pilot_page_flightlog(df, pilot_dropdown):
    if pilot_dropdown == '⌀ All Pilots': # If All Pilots are selected
        df = df.iloc[:, 1:].mean().to_frame().T
    else:
        df = df[df['Pilot']==pilot_dropdown]

    if len(df)==1:
        # Pilots Flight Time
        sum_flight_time = df.iloc[0]["Total_Flight_Time"]
        # Pilots Number of Flights
        sum_block_time = df.iloc[0]["Total_Block_Time"]
        # Pilots Flight to Block Time
        flight_block_ratio = df.iloc[0]["Flight_Block_Ratio"]
        # Pilots Number of Flights
        sum_flights = df.iloc[0]["Number_of_Flights"]
        # Pilots Landings
        sum_landings = df.iloc[0]["Number_of_Landings"]
    else:
        sum_flight_time, sum_block_time, flight_block_ratio, \
            sum_flights, sum_landings = ('NO DATA',) * 5

    return sum_flight_time, sum_block_time, flight_block_ratio,\
        sum_flights, sum_landings

def select_pilot_page_reservationlog(df, df_trend, pilot_dropdown):
    selected = sum_pilot_page_reservationlog(df, pilot_dropdown)  # Extract KPI specific Data
    selected_t_minus = sum_pilot_page_reservationlog(df_trend, pilot_dropdown)  # Extract KPI - one Year Data

    return selected, selected_t_minus

def sum_pilot_page_reservationlog(df, pilot_dropdown):
    if pilot_dropdown == '⌀ All Pilots':  # If all Pilots are Selected
        df = df.iloc[:, 1:].mean().to_frame().T
    else:
        df = df[df['Pilot']==pilot_dropdown]

    if len(df)==1:
        # Pilots Cancelled Reservation
        reservations = df.iloc[0]["Reservations"]
        # Pilots Cancelled Reservation
        cancelled = df.iloc[0]["Cancelled"]
    else:  # If Data is empty
        reservations, cancelled = ('NO DATA',) * 2

    return reservations, cancelled

def select_pilot_page_flight_reservation_log(df, df_trend, pilot_dropdown):
    selected = sum_pilot_page_flight_reservation_log(df, pilot_dropdown)  # Extract KPI specific Data
    selected_t_minus = sum_pilot_page_flight_reservation_log(df_trend, pilot_dropdown)  # Extract KPI - one Year Data

    return selected, selected_t_minus

def sum_pilot_page_flight_reservation_log(df, pilot_dropdown):
    if pilot_dropdown == '⌀ All Pilots':  # If all Pilots are selected
        df = df.iloc[:, 1:].mean().to_frame().T  # Calculate Mean of Columns and transform
    else:
        df = df[df['Pilot']==pilot_dropdown]

    if len(df)==1:
        # Pilots Reservations to Flighttime
        res_flight_time = df.iloc[0]["Flight_to_Reservation_Time"]
        # Pilots Cancelled Ratio
        cancelled_ratio = df.iloc[0]["Ratio_Cancelled"]
    else:  # If no Data is given
        res_flight_time, cancelled_ratio = ('NO DATA',) * 2

    return res_flight_time, cancelled_ratio

#--------------------------------- Aircraft Page ----------------------------------------
# Flightlog
def select_aircraft_page_flightlog(df, df_trend, aircraft_dropdown):
    selected = sum_aircraft_page_flightlog(df, aircraft_dropdown) # Extract KPI specific Data
    selected_t_minus = sum_aircraft_page_flightlog(df_trend, aircraft_dropdown) # Extract KPI - one Year Data
    return selected, selected_t_minus

def sum_aircraft_page_flightlog(df, aircraft_dropdown):
    if aircraft_dropdown == '⌀ All Aircrafts':
        df = df.iloc[:, 1:].mean().to_frame().T
    else:
        df = df[df['Aircraft']==aircraft_dropdown]

    if len(df) == 1:
        # Aircraft-Flight-Hours
        sum_flight_time = df.iloc[0]["Total_Flight_Time"]
        # Aircraft-Number-of-Flights
        sum_flights = df.iloc[0]["Number_of_Flights"]
        # Aircraft-Mean-Flight-Time
        mean_flight_time = df.iloc[0]["Mean_Flight_Time"]
        # Aircraft-Number-of-Landings
        sum_landings = df.iloc[0]["Number_of_Landings"]
        # Aircraft-Number-of-Airports
        sum_airports = df.iloc[0]["Number_of_Different_Airports"]
        # Aircraft-Fuel-per-Hour
        fuel_per_hour = df.iloc[0]["Fuel_per_hour"]
        # Aircraft-Oil-per-Hour
        oil_per_hour = df.iloc[0]["Oil_per_hour"]
        # Aircraft-Instruction-Ratio
        instruction_ratio = df.iloc[0]["Instruction_Ratio"]
        # Aircraft-Number-of-Pilots
        sum_pilots = df.iloc[0]["Number_of_Pilots"]
    else:
        sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots = (0,) * 9

    return sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots

# ---------------------------------- School Page ----------------------------------------
def select_school_page_trainee_instructorlog(df, df_trend, dropdown):
    selected = sum_school_page_trainee_instructorlog(df, dropdown) # Extract KPI specific Data
    selected_t_minus = sum_school_page_trainee_instructorlog(df_trend, dropdown) # Extract KPI - one Year Data
    return selected, selected_t_minus

def sum_school_page_trainee_instructorlog(df, dropdown):

    if dropdown == 'Σ All Trainees':
        df = df.iloc[:, 1:].sum().to_frame().T
    else:
        df = df[df['Pilot']==dropdown]

    if len(df)==1:
        # Pilots Flight Time
        instruction_hours_trainee = df.iloc[0]["Total_Duration"]
        # Pilots Number of Flights
        trainings_sets_trainee = df.iloc[0]["Number_of_Instructions"]
    else:
        instruction_hours_trainee, trainings_sets_trainee = ('NO DATA',) * 2

    return instruction_hours_trainee, trainings_sets_trainee

def select_school_page_instructor_instructorlog(df, df_trend, dropdown):
    selected = sum_school_page_instructor_instructorlog(df, dropdown) # Extract KPI specific Data
    selected_t_minus = sum_school_page_instructor_instructorlog(df_trend, dropdown) # Extract KPI - one Year Data
    return selected, selected_t_minus

def sum_school_page_instructor_instructorlog(df, dropdown):

    if dropdown == 'Σ All Instructors':
        df = df.iloc[:, 1:].sum().to_frame().T
    else:
        df = df[df['Instructor']==dropdown]

    if len(df)==1:
        # Pilots Flight Time
        instruction_hours_instructor = df.iloc[0]["Total_Duration"]
        # Pilots Number of Flights
        trainees_per_instructor = df.iloc[0]["Number_of_Different_Pilots"]
    else:
        instruction_hours_instructor, trainees_per_instructor = ('NO DATA',) * 2

    return instruction_hours_instructor, trainees_per_instructor
