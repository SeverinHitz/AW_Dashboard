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
    trend_strings, trend_styles = sf.trend_string(trend)

    return trend_strings, trend_styles

######################### Overview Page ###############################

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


################################### Aircraft Page #########################################
# Flightlog
def select_aircraft_page_flightlog(df, df_trend, aircraft_dropdown):
    selected = sum_aircraft_page_flightlog(df, aircraft_dropdown) # Extract KPI specific Data
    selected_t_minus = sum_aircraft_page_flightlog(df_trend, aircraft_dropdown) # Extract KPI - one Year Data
    return selected, selected_t_minus

def sum_aircraft_page_flightlog(df, aircraft_dropdown):
    if aircraft_dropdown == '⌀ All Aircrafts':
        agg_aircraft_df = df.iloc[:, 1:].mean().to_frame().T
    else:
        agg_aircraft_df = df[df['Aircraft']==aircraft_dropdown]

    if len(agg_aircraft_df) == 1:
        # Aircraft-Flight-Hours
        sum_flight_time = agg_aircraft_df.iloc[0]["Total_Flight_Time"]
        # Aircraft-Number-of-Flights
        sum_flights = agg_aircraft_df.iloc[0]["Number_of_Flights"]
        # Aircraft-Mean-Flight-Time
        mean_flight_time = agg_aircraft_df.iloc[0]["Mean_Flight_Time"]
        # Aircraft-Number-of-Landings
        sum_landings = agg_aircraft_df.iloc[0]["Number_of_Landings"]
        # Aircraft-Number-of-Airports
        sum_airports = agg_aircraft_df.iloc[0]["Number_of_Different_Airports"]
        # Aircraft-Fuel-per-Hour
        fuel_per_hour = agg_aircraft_df.iloc[0]["Fuel_per_hour"]
        # Aircraft-Oil-per-Hour
        oil_per_hour = agg_aircraft_df.iloc[0]["Oil_per_hour"]
        # Aircraft-Instruction-Ratio
        instruction_ratio = agg_aircraft_df.iloc[0]["Instruction_Ratio"]
        # Aircraft-Number-of-Pilots
        sum_pilots = agg_aircraft_df.iloc[0]["Number_of_Pilots"]
    else:
        sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots = (0,) * 9

    return sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots
