from icecream import ic

def trend_string(len_selected, trends=None):
    # Create the Trendstring
    trend_strings = ('trend n/a',) * len_selected
    trend_styles = ({'color': 'grey'},) * len_selected

    if trends is not None:
        trend_strings = []
        trend_styles = []
        for trend in trends:
            if trend > 0:
                trend_strings.append(f'↗ {trend:.2f} %')
                trend_styles.append({'color': 'lightgreen'})
            elif trend < 0:
                trend_strings.append(f'↘ {trend:.2f} %')
                trend_styles.append({'color': 'red'})
            else:
                trend_strings.append(f'→ {trend:.2f} %')
                trend_styles.append({'color': 'yellow'})

    return trend_strings, trend_styles


# ------------------------------------------- Overview page ---------------------------------------

# Flightlog
def trend_string_overview_page_flightlog(selected):
    # Flight Time
    hours = selected[0] // 60
    minutes = selected[0] % 60
    formatted_time = f'{int(hours):02d}:{int(minutes):02d}'
    sum_total = f'{formatted_time} h'

    # Number of Flights:
    sum_flight = f'{selected[1]} #'

    # Number of Landings
    sum_landings = f'{selected[2]:.0f} #'

    # Fuel Used
    sum_fuel = f'{selected[3]:.0f} L'

    return sum_total, sum_flight, sum_landings, sum_fuel

# Instructorlog:
def trend_string_overview_page_instructorlog(selected):
    # Instructor Time
    hours = selected[0] // 60
    minutes = selected[0] % 60
    formatted_time = f'{int(hours):02d}:{int(minutes):02d}'
    sum_total = f'{formatted_time} h'

    # Number of Trainees:
    sum_trainees = f'{selected[1]} #'

    # Number of Instructionsets
    sum_instruction_sets = f'{selected[2]:.0f} #'

    return sum_total, sum_trainees, sum_instruction_sets

# ------------------------------- Pilot Page ---------------------------------------

def trend_string_pilot_page_flightlog(selected):
    # Pilots Flight Time
    sum_flight_time = f'{selected[0]:.1f} h'
    # Pilots Number of Flights
    sum_block_time = f'{selected[1]:.1f} h'
    # Pilots Flight to Block Time
    flight_block_ratio = f'{selected[2] * 100:.2f} %'
    # Pilots Number of Flights
    sum_flights = f'{selected[3]:.0f} #'
    # Pilots Landings
    sum_landings = f'{selected[4]:.0f} #'

    return sum_flight_time, sum_block_time, flight_block_ratio, \
        sum_flights, sum_landings

def trend_string_pilot_page_reservationlog(selected):
    # Pilots Cancelled Reservation
    reservations = f'{selected[0]:.0f} #'
    # Pilots Cancelled Reservation
    cancelled = f'{selected[1]:.0f} #'

    return reservations, cancelled

def trend_string_pilot_page_flight_reservation_log(selected):
    # Pilots Reservations to Flighttime
    res_flight_time = f'{selected[0] * 100:.2f} %'
    # Pilots Cancelled Ratio
    cancelled_ratio = f'{selected[1] * 100:.2f} %'

    return res_flight_time, cancelled_ratio
#-------------------------------- Aircraft Page ------------------------------------

def trend_string_aircraft_page_flightlog(selected):
    # Aircraft-Flight-Hours
    sum_flight_time = f'{selected[0]:.1f} h'
    # Aircraft-Number-of-Flights
    sum_flights = f'{selected[1]:.0f} #'
    # Aircraft-Mean-Flight-Time
    mean_flight_time = f'{selected[2] * 60:.0f} min'
    # Aircraft-Number-of-Landings
    sum_landings = f'{selected[3]:.0f} #'
    # Aircraft-Number-of-Airports
    sum_airports = f'{selected[4]:.0f} #'
    # Aircraft-Fuel-per-Hour
    fuel_per_hour = f'{selected[5]:.1f} L'
    # Aircraft-Oil-per-Hour
    oil_per_hour = f'{selected[6] * 1000:.0f} mL'
    # Aircraft-Instruction-Ratio
    instruction_ratio = f'{selected[7] * 100:.1f} %'
    # Aircraft-Number-of-Pilots
    sum_pilots = f'{selected[8]:.0f} #'

    return sum_flight_time, sum_flights, mean_flight_time, sum_landings, \
            sum_airports, fuel_per_hour, oil_per_hour, instruction_ratio, sum_pilots

# ------------------------------ School Page ----------------------------------
def trend_string_school_page_trainee_instructorlog(selected):
    # Pilots Flight Time
    instruction_hours_trainee = f'{selected[0]:.1f} h'
    # Pilots Number of Flights
    trainings_sets_trainee = f'{selected[0]:.0f} #'

    return instruction_hours_trainee, trainings_sets_trainee

def trend_string_school_page_instructor_instructorlog(selected):
    # Pilots Flight Time
    instruction_hours_instructor = f'{selected[0]:.1f} h'
    # Pilots Number of Flights
    trainees_per_instructor = f'{selected[1]:.0f} #'

    return instruction_hours_instructor, trainees_per_instructor

