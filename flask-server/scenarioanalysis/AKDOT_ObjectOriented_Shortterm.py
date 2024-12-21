import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, timedelta
import simpy
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
from datetime import datetime
import matplotlib.pyplot as plt
from IPython.display import display
from scenarioanalysis import *
from flask import current_app
import os
import json

class TrafficDataProcessor:
    def __init__(self, excel_file, block_start_date, block_start_hour, block_duration):
        self.excel_file = excel_file
        self.block_start_date = datetime.strptime(block_start_date, '%d %b %Y')
        self.block_start_hour = block_start_hour
        self.block_duration = block_duration
        self.data = self.load_and_process_data()

    def load_and_process_data(self):
        processed_data = {}
        with pd.ExcelFile(self.excel_file) as xls:
            for sheet_name in xls.sheet_names:
                try:
                    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                    month, year = self.parse_sheet_name(sheet_name)
                    self.process_sheet_data(df, month, year, processed_data)
                except ValueError as e:
                    print(f"Error processing '{sheet_name}': {e}")
        return processed_data

    @staticmethod
    def parse_sheet_name(sheet_name):
        month, year = sheet_name.strip().split('-')
        year = int(year.strip())
        month = datetime.strptime(month.strip(), '%b').month
        return month, year

    def process_sheet_data(self, df, month, year, processed_data):
        days_in_month = calendar.monthrange(year, month)[1]
        start_day_of_week = datetime(year, month, 1).weekday()
        for day in range(1, days_in_month + 1):
            day_of_week = calendar.day_name[(start_day_of_week + day - 1) % 7]
            for hour in range(df.shape[0]):
                value = df.iloc[hour, day-1] if day-1 < df.shape[1] else np.nan
                if pd.notna(value) and value != -1:
                    key = (month, day_of_week, hour)
                    processed_data.setdefault(key, []).append(value)

    def arrival_rates(self, month, day_of_week, hour):
        key = (month, day_of_week, hour)
        if key in self.data:
            values = np.array(self.data[key])
            return values.mean(), values.var()
        return None

    def generate_cumulative_arrival_times(self):
        cumulative_arrival_times = []
        # Extract month and day of week from block start date
        month = self.block_start_date.month
        day_of_week = calendar.day_name[self.block_start_date.weekday()]

        # Calculate total hours based on block duration (converted to hours from seconds)
        total_hours = 2 + self.block_duration / 3600 + 6  # 2 hours before the block + duration + 6 hours after

        clock = 0
        for offset_hour in range(int(self.block_start_hour - 2), int(self.block_start_hour - 2 + total_hours)):
            normalized_hour = offset_hour % 24
            num_arrivals = self.generate_normal_arrival_times(month, day_of_week, normalized_hour)

            if num_arrivals > 0:
                arrival_times_int = np.round(np.random.uniform(0, 3600, num_arrivals)).astype(int)
                actual_times_int = sorted(arrival_times_int + clock * 3600)
                cumulative_arrival_times.extend(actual_times_int)
                clock += 1

        # Sort and convert the final list to a numpy array for return
        return cumulative_arrival_times

    def generate_normal_arrival_times(self, month, day_of_week, normalized_hour):
        rate_info = self.arrival_rates(month, day_of_week, normalized_hour)
        if rate_info is None:
            return np.array([])

        mean_rate, var_rate = rate_info
        if mean_rate <= 0:
            return np.array([])

        # Use normal distribution to generate the total number of arrivals for the hour
        num_arrivals = np.random.normal(mean_rate, np.sqrt(var_rate))
        # Ensure the number of arrivals is not negative
        num_arrivals = max(0, round(num_arrivals))

        return num_arrivals


class Vehicle:
    def __init__(self, env, name, vehicle_type, check_in, Marathon_gate, Bluff_gate, global_waiting_times_normal, global_waiting_times_no_reaction, global_waiting_times_taking_detour, global_cycle_times_normal, global_cycle_times_no_reaction, global_cycle_times_taking_detour, hazmat_waits, num_of_vehicles, num_of_trucks, num_of_hazmat, hazmat_lane, block, route, reaction_time, block_start_sec, block_end_sec):
        self.env = env
        self.name = name
        self.vehicle_type = vehicle_type
        self.check_in = check_in
        self.Marathon_gate = Marathon_gate
        self.Bluff_gate = Bluff_gate
        self.global_waiting_times_normal = global_waiting_times_normal
        self.global_waiting_times_no_reaction = global_waiting_times_no_reaction
        self.global_waiting_times_taking_detour = global_waiting_times_taking_detour
        self.global_cycle_times_normal = global_cycle_times_normal
        self.global_cycle_times_no_reaction = global_cycle_times_no_reaction
        self.global_cycle_times_taking_detour = global_cycle_times_taking_detour
        self.hazmat_waits = hazmat_waits
        self.num_of_vehicles = num_of_vehicles
        self.num_of_trucks = num_of_trucks
        self.num_of_hazmat = num_of_hazmat
        self.hazmat_lane = hazmat_lane
        self.block_start_sec = block_start_sec
        self.block_end_sec = block_end_sec
        self.block = block
        self.route = route
        self.reaction_time = reaction_time

        # Set initial routes
        self.initial_route_to_matson = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Matson']
        self.initial_route_from_matson = ['Second Fork to Matson', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']
        self.initial_route_to_tote = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Tote']
        self.initial_route_from_tote = ['Second Fork to Tote', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']

    def set_alternate_routes(self):
        if self.block == 'Section 1':
            if self.route == 'Insulfoam-Insulfoam':
                self.route_to_matson = [
                    'Insulfoam to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = [
                    'Second Fork to Matson',
                    'First Fork to Second Fork',
                    'Gate to First Fork',
                    'Insulfoam to Gate'
                ]
                self.route_to_tote = [
                    'Insulfoam to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Second Fork to Tote',
                    'First Fork to Second Fork',
                    'Gate to First Fork',
                    'Insulfoam to Gate'
                ]

            elif self.route == 'Insulfoam-Military':
                self.route_to_matson = [
                    'Insulfoam to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = [
                    'Insulfoam to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Military-Insulfoam':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = [
                    'Insulfoam to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = [
                    'Insulfoam to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = ['Tote to Military']

            elif self.route == 'Military-Military':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = ['Tote to Military']

        elif self.block == 'Section 2':

            if self.route == 'Marathon-Military':
                self.route_to_matson = ['Marathon to Matson']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = ['Marathon to second Fork', 'Second Fork to Tote']
                self.route_from_tote = ['Tote to Military']

            elif self.route == 'Marathon-Marathon':
                self.route_to_matson = ['Marathon to Matson']
                self.route_from_matson = ['Marathon to Matson']
                self.route_to_tote = ['Marathon to second Fork', 'Second Fork to Tote']
                self.route_from_tote = ['Marathon to second Fork', 'Second Fork to Tote']

            elif self.route == 'Military-Marathon':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['Marathon to Matson']
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = ['Marathon to second Fork', 'Second Fork to Tote']

            elif self.route == 'Military-Military':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = ['Tote to Military']

            elif self.route == 'Bluff-Marathon':
                self.route_to_matson = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = ['Marathon to Matson']
                self.route_to_tote = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = ['Marathon to second Fork', 'Second Fork to Tote']

            elif self.route == 'Marathon-Bluff':
                self.route_to_matson = ['Marathon to Matson']
                self.route_from_matson = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = ['Marathon to second Fork', 'Second Fork to Tote']
                self.route_from_tote = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Bluff-Military':
                self.route_to_matson = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = ['Marathon to Matson']
                self.route_to_tote = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = ['Marathon to second Fork', 'Second Fork to Tote']

            elif self.route == 'Military-Bluff':
                self.route_to_matson = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = ['Marathon to Matson']
                self.route_to_tote = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = ['Marathon to second Fork', 'Second Fork to Tote']

            elif self.route == 'Bluff-Bluff':
                self.route_to_matson = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = ['Marathon to Matson']
                self.route_to_tote = [
                    'Bluff to first fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = ['Marathon to second Fork', 'Second Fork to Tote']

            elif self.route == 'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = ['hybrid to Tote']
                self.route_from_tote = ['hybrid to Tote']

        elif self.block == 'Section 3':
            if self.route == 'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = ['hybrid to Tote']
                self.route_from_tote = ['hybrid to Tote']

            elif self.route == 'Marathon Transit Area Hybrid-Military':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = ['hybrid to Tote']
                self.route_from_tote = ['Matson to Tote']

            elif self.route == 'Military-Marathon Transit Area Hybrid':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = ['Matson to Tote']
                self.route_from_tote = ['hybrid to Tote']

            elif self.route == 'Military-Military':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = ['Tote to Military']

        elif self.block == 'Section 4':
            if self.route == 'ABI-Roger':
                self.route_to_matson = [
                    'Gate to First Fork',
                    'First Fork to Matson through ABI'
                ]
                self.route_from_matson = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Matson'
                ]
                self.route_to_tote = [
                    'Gate to First Fork',
                    'First Fork to Second Fork through ABI',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Tote'
                ]

            elif self.route == 'Roger-ABI':
                self.route_to_matson = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Matson'
                ]
                self.route_from_matson = [
                    'Gate to First Fork',
                    'First Fork to Matson through ABI'
                ]
                self.route_to_tote = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Tote'
                ]
                self.route_from_tote = [
                    'Gate to First Fork',
                    'First Fork to Second Fork through ABI',
                    'Second Fork to Tote'
                ]

            elif self.route == 'ABI-ABI':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Matson through ABI'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Matson through ABI'
                ]
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork through ABI',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork through ABI',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Roger-Roger':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Tote'
                ]
                self.route_from_tote = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Tote'
                ]

            elif self.route == 'ABI-Military':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Matson through ABI'
                ]
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork through ABI',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = ['Tote to Military']

            elif self.route == 'Military-ABI':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Matson through ABI'
                ]
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork through ABI',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Military-Military':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = ['Tote to Military']

            elif self.route == 'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = ['hybrid to Tote']
                self.route_from_tote = ['hybrid to Tote']

        elif self.block == 'Section 5':
            if self.route == 'Military-Military':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = ['Tote to Military']

            elif self.route == 'Roger-Military':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Tote'
                ]
                self.route_from_tote = ['Tote to Military']

            elif self.route == 'Military-Roger':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = [
                    'Gate to First Fork',
                    'Roger',
                    'Roger to Tote'
                ]

        elif self.block == 'Section 6':
            if self.route == 'Transit-Transit':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote through Transit'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote through Transit'
                ]

            elif self.route == 'Military-Military':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson'
                ]
                self.route_to_tote = ['Tote to Military']
                self.route_from_tote = ['Tote to Military']

        elif self.block == 'Section 7':
            if self.route == 'Marathon Transit Area Hybrid-Military':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Military-Marathon Transit Area Hybrid':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Military-Military':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Tidewater-Tidewater':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson through Tidewater'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson through Tidewater'
                ]
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'PetroStar-Tidewater':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'PetroStar',
                    'PetroStar to Matson'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson through Tidewater'
                ]
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Tidewater-PetroStar':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson through Tidewater'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'PetroStar',
                    'PetroStar to Matson'
                ]
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

        elif self.block == 'Section 8':
            if self.route == 'Tidewater-Tidewater':
                self.route_to_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson through Tidewater'
                ]
                self.route_from_matson = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Matson through Tidewater'
                ]
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Marathon Transit Area Hybrid-Military':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid':
                self.route_to_matson = ['hybrid to Matson']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Military-Marathon Transit Area Hybrid':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['hybrid to Matson']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]

            elif self.route == 'Military-Military':
                self.route_to_matson = ['Matson to Military']
                self.route_from_matson = ['Matson to Military']
                self.route_to_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
                self.route_from_tote = [
                    'Ocean to Gate',
                    'Gate to First Fork',
                    'First Fork to Second Fork',
                    'Second Fork to Tote'
                ]
        #if self.block == 'Section 9':
        #  if self.route == 'Main Route-Main Route':
        #    self.route_to_matson = self.initial_route_to_matson
        #    self.route_from_matson = self.initial_route_from_matson
        #    self.route_to_tote = self.initial_route_to_tote
        #    self.route_from_tote = self.initial_route_from_tote

        if self.block == 'None':
            self.route_to_matson = self.initial_route_to_matson
            self.route_from_matson = self.initial_route_from_matson
            self.route_to_tote = self.initial_route_to_tote
            self.route_from_tote = self.initial_route_from_tote

    def stop_for_blockage(self):
        wait_time = 0
        if self.block_start_sec <= self.env.now <= self.block_end_sec:
            wait_time = self.block_end_sec - self.env.now

        return wait_time

    def select_route_based_on_condition(self, destination):
        # Check if the current time is beyond the block start and adjust block status
        if self.env.now < self.block_start_sec:
            self.block = 'None'
            # Using alternate routes
            self.set_alternate_routes()
            if destination == 1:
                route_to = self.route_to_matson
                route_from = self.route_from_matson
            else:  # destination == 2
                route_to = self.route_to_tote
                route_from = self.route_from_tote

        # Using primary routes
        if self.env.now <= self.block_start_sec + self.reaction_time:
            if destination == 1:
                route_to = self.initial_route_to_matson
                route_from = self.initial_route_from_matson
            else:  # destination == 2
                route_to = self.initial_route_to_tote
                route_from = self.initial_route_from_tote
        else:
            # Using alternate routes
            self.set_alternate_routes()
            if destination == 1:
                route_to = self.route_to_matson
                route_from = self.route_from_matson
            else:  # destination == 2
                route_to = self.route_to_tote
                route_from = self.route_from_tote

        return route_to, route_from


    def is_affected_by_blockage(self, segment):
        blockage_segments = {
            'Section 1': 'Ocean to Gate',
            'Section 2': 'Gate to First Fork',
            'Section 3': 'First Fork to Second Fork',
            'Section 4': 'First Fork to Second Fork',
            'Section 5': 'Second Fork to Tote',
            'Section 6': 'Second Fork to Tote',
            'Section 7': 'Second Fork to Matson',
            'Section 8': 'Second Fork to Matson',
            'Section 9': 'hybrid to Matson'
        }

        for key, value in blockage_segments.items():
            if segment == value and self.block == key:
                return True
        return False

    def compute_no_reaction_waiting_time(self):
        self.first_route = self.initial_route_to_matson if self.destination == 1 else self.initial_route_to_tote
        self.second_route = self.initial_route_from_matson if self.destination == 1 else self.initial_route_from_tote

        affected = False
        for segment in self.first_route + self.second_route:
            if self.is_affected_by_blockage(segment):
                affected = True
                break
        if affected:
            waiting_time = self.block_end_sec - self.arrival_time
        else:
            waiting_time = self.exit_the_port - self.arrival_time - self.transportation_time(self.first_route) - self.transportation_time(self.second_route) - self.unloading_loading - self.haz_pross - self.maintenance_process
        return waiting_time

    def compute_no_reaction_cycle_time(self):
        self.first_route = self.initial_route_to_matson if self.destination == 1 else self.initial_route_to_tote
        self.second_route = self.initial_route_from_matson if self.destination == 1 else self.initial_route_from_tote

        affected = False
        for segment in self.first_route + self.second_route:
            if self.is_affected_by_blockage(segment):
                affected = True
                break
        if affected:
          cycle_time = self.block_end_sec - self.arrival_time + self.transportation_time(self.first_route) + self.transportation_time(self.second_route) + self.unloading_loading + self.haz_pross + self.maintenance_process
        else:
          cycle_time = self.exit_the_port - self.arrival_time
        return cycle_time

    def transportation_time(self, route):
        # Map of standard travel times for each part of the route
        standard_travel_times = {
            'Ocean to Gate': 0.26 * 3600 / 20,
            'Insulfoam to Gate': 0.45 * 3600 / 15,
            'Gate to First Fork': 0.18 * 3600 / 20,
            'First Fork to Second Fork': 0.14 * 3600 / 20,
            'First Fork to Second Fork through ABI': 0.54 * 3600 / 15,
            'First Fork to Matson through ABI': 0.65 * 3600 / 10,
            'Bluff to first fork': 1.9*3600/20,
            'Tote to Military': 0.6 * 3600 / 20,
            'hybrid to Matson': 1.23*3600/15,
            'hybrid to Tote': 1.75*3600/15,
            'Roger': 0.2 * 3600 / 15,
            'Roger to Tote': 0.68 * 3600 / 20,
            'Roger to Matson': 0.48 * 3600 / 20,
            'PetroStar': 0.1 * 3600 / 5,
            'PetroStar to Matson': 0.3 * 3600 / 20,
            'Second Fork to Tote through Transit': 0.71 * 3600 / 15,
            'Matson to Military': 0.67 * 3600 / 20,
            'Marathon to Matson': 1.07 * 3600 / 15,
            'Marathon to second Fork': 0.8 * 3600 / 15,
            'First Fork to Tote through Roger Graves Rd': 0.83 * 3600 / 20,
            'Second Fork to Matson': 0.4 * 3600 / 20,
            'Second Fork to Matson through Tidewater': 0.4 * 3600 / 15,
            'Second Fork to Tote': 0.7 * 3600 / 20} 

        # Calculating the standard time for the entire route
        time = sum(standard_travel_times.get(street, 0) for street in route)

        # Calculating the current simulation seconds and converting it to hours and months
        simulation_second = self.env.now
        hour = (simulation_second // 3600) % 24
        day_of_year = (simulation_second // 86400) % 365
        month = (day_of_year // 30) + 1
        is_night = 19 <= hour or hour <= 7

        # Time adjustment factors based on the month
        month_time_factors = {
            1: 1.10, 2: 1.10, 3: 1.05, 4: 1.00,
            5: 0.90, 6: 0.80, 7: 0.80, 8: 0.80,
            9: 0.90, 10: 1.00, 11: 1.05, 12: 1.10}

        # Adjusting time based on the month and night conditions
        time *= month_time_factors.get(month, 1)
        if is_night:
            time *= 1.1

        # Returning the calculated time
        return time

    def run(self, arrival_time):
        yield self.env.timeout(arrival_time)
        #print(f"{self.name} arrived at {self.env.now}")
        self.arrival_time = self.env.now

        # Determine the destination for Trucks and Cars
        if self.vehicle_type == 'Truck':
            self.destination = random.randint(1, 2)
        else:
            self.destination = 1 if random.random() < 0.5 else 2

        # Determine the route based on current conditions and destination
        route_to, route_from = self.select_route_based_on_condition(self.destination)

        # Check the first segment and use the appropriate gate
        first_segment = route_to[0]
        if first_segment == 'Marathon to Matson' or first_segment == 'Marathon to Tote':
            with self.Marathon_gate.request() as Marathon_request:
                yield Marathon_request
                yield self.env.timeout(np.round(random.randint(10,20)))
                self.enter_the_port = self.env.now

        elif first_segment == 'Bluff gate to first fork':
            with self.Bluff_gate.request() as Bluff_gate_request:
                yield Bluff_gate_request
                yield self.env.timeout(np.round(random.randint(10,20)))
                self.enter_the_port = self.env.now

        else:
            with self.check_in.request() as check_in_request:
                yield check_in_request
                yield self.env.timeout(np.round(random.randint(10,20)))
                self.enter_the_port = self.env.now

        for segment in route_to:
            # Check for blockage and handle it if not already encountered
            if self.is_affected_by_blockage(segment):
                yield self.env.timeout(self.stop_for_blockage())
                break  # After encountering a blockage, no need to check further

        # Logic for processing at the destination for Trucks
        if self.vehicle_type == 'Truck':
            enter_containeryard_time = self.env.now

            time_ranges = [(600, 750), (500, 600), (900, 1200)]
            probabilities = [0.5, 0.3, 0.2]

            selected_range = random.choices(time_ranges, probabilities, k=1)[0]

            self.unloading_loading = random.randint(selected_range[0], selected_range[1])

            yield self.env.timeout(self.unloading_loading)
            finish_unloading_loading = self.env.now

            # Process in hazmat lane if required
            if random.random() < 0.125:
                with self.hazmat_lane.request() as hazmat_request:
                    hazmat_arrive = self.env.now
                    yield hazmat_request
                    hazmat_enter = self.env.now
                    hazmat_process = random.randint(5, 15)
                    yield self.env.timeout(hazmat_process)
                    hazmat_end = self.env.now
                    hazmat_wait = hazmat_enter - hazmat_arrive
                    self.haz_pross = hazmat_end - hazmat_enter
                    self.hazmat_waits.append(hazmat_wait)
                    self.num_of_hazmat +=1
            else:
                self.haz_pross = 0

            # Maintenance if required
            if random.random() < 0.1:
                self.maintenance_process = random.randint(600, 900)
                yield self.env.timeout(self.maintenance_process)
            else:
              self.maintenance_process = 0
        else:
          self.unloading_loading = 0
          self.maintenance_process = 0
          self.haz_pross = 0

        # Compute Travel Time
        yield self.env.timeout(self.transportation_time(route_to))

        # Process the route from the destination, ensuring blockage is handled only if not encountered before
        for segment in route_from:
            if  self.is_affected_by_blockage(segment):
                yield self.env.timeout(self.stop_for_blockage())
                break

        # Compute return Travel Time
        yield self.env.timeout(self.transportation_time(route_from))
        self.exit_the_port = self.env.now

        # Calculate waiting and cycle times
        cycle_time = self.env.now - self.arrival_time
        waiting_time = cycle_time - self.transportation_time(route_to) - self.transportation_time(route_from) - self.unloading_loading - self.haz_pross - self.maintenance_process

        no_reaction_waiting_time = self.compute_no_reaction_waiting_time()
        no_reaction_cycle = self.compute_no_reaction_cycle_time()

        # Update the global waiting and cycle times

        if self.arrival_time < self.block_start_sec:
            # If the current time is before the blockage
            self.global_waiting_times_normal.append(waiting_time)
            if self.vehicle_type == 'Truck':
                self.global_cycle_times_normal.append(cycle_time)

        elif self.block_start_sec + self.reaction_time <= self.arrival_time <= self.block_end_sec:
            # If the current time is after the blockage but before Reaction Time
            self.global_waiting_times_taking_detour.append(waiting_time)
            if self.vehicle_type == 'Truck':
                self.global_cycle_times_taking_detour.append(cycle_time)

        if self.block_start_sec <= self.arrival_time <= self.block_end_sec:
            if self.vehicle_type == 'Truck':
                self.global_waiting_times_no_reaction.append(no_reaction_waiting_time)
                self.global_cycle_times_no_reaction.append(no_reaction_cycle)


class Environment:
    def __init__(self, block, block_start_sec, block_end_sec, reaction_time):
        self.env = simpy.Environment()
        self.check_in = simpy.Resource(self.env, capacity=1)
        self.Marathon_gate = simpy.Resource(self.env, capacity=1)
        self.Bluff_gate = simpy.Resource(self.env, capacity=1)
        self.hazmat_lane = simpy.Resource(self.env, capacity=1)
        self.reaction_time = reaction_time

        # Add the block attribute
        self.block = block

        # Lists to store separated times for three conditions
        self.global_waiting_times_normal = []
        self.global_cycle_times_normal = []
        self.global_waiting_times_no_reaction = []
        self.global_cycle_times_no_reaction = []
        self.global_waiting_times_taking_detour = []
        self.global_cycle_times_taking_detour = []
        self.hazmat_waits = []

        # Use simple counters for the number of vehicles
        self.total_num_of_vehicles = 0
        self.total_num_of_trucks = 0
        self.total_num_of_hazmat = 0

        # Initialize block variables
        self.block_start_sec = block_start_sec
        self.block_end_sec = block_end_sec

    def add_vehicle(self, name, arrival_time, vehicle_type, route):
        # Increment counters based on vehicle type
        self.total_num_of_vehicles += 1
        if vehicle_type == 'Truck':
            self.total_num_of_trucks += 1
        elif vehicle_type == 'Hazmat':
            self.total_num_of_hazmat += 1

        vehicle = Vehicle(self.env, name, vehicle_type, self.check_in, self.Marathon_gate, self.Bluff_gate, self.global_waiting_times_normal, self.global_waiting_times_no_reaction, self.global_waiting_times_taking_detour, self.global_cycle_times_normal, self.global_cycle_times_no_reaction, self.global_cycle_times_taking_detour, self.hazmat_waits, self.total_num_of_vehicles, self.total_num_of_trucks, self.total_num_of_hazmat, self.hazmat_lane, self.block, route, self.reaction_time, self.block_start_sec, self.block_end_sec)
        self.env.process(vehicle.run(arrival_time))


def parse_date_string(block_date):
  # Parse the date string into a datetime object
  date_object = datetime.strptime(block_date, '%d %b %Y')

  # Extract the month as a string
  month = date_object.strftime('%b')

  # Get the day of the week, adjusting to make Monday = 0
  day_of_week = (date_object.weekday() + 1) % 7  # Python's datetime treats Monday as 0, so we adjust to make Monday = 0 following your specification

  return month, day_of_week

def setup_simulation(excel_file_trucks, excel_file_cars, block, route, block_duration_type, block_start_date, block_start_hour, reaction_time):

    block_start_sec = 7200  # Assuming block starts 2 hours after the simulation starts

    if block_duration_type == 'short':
      block_duration = random.randint(15*60, 30*60)  # Between 15 to 30 minutes
    elif block_duration_type == 'medium':
      block_duration = random.randint(30*60, 120*60)  # Between 30 minutes to 2 hours
    elif block_duration_type == 'long':
      block_duration = random.randint(120*60, 240*60)  # Between 2 to 4 hours

    block_end_sec = block_start_sec + block_duration

    processor_truck = TrafficDataProcessor(excel_file_trucks, block_start_date, block_start_hour, block_duration)
    processor_car = TrafficDataProcessor(excel_file_cars, block_start_date, block_start_hour, block_duration)
    truck_arrival_times = processor_truck.generate_cumulative_arrival_times()
    car_arrival_times = processor_car.generate_cumulative_arrival_times()

    env = Environment(block, block_start_sec, block_end_sec, reaction_time)

    month, day_of_week = parse_date_string(block_start_date)

    # Add vehicles to the simulation
    for i, arrival_time in enumerate(truck_arrival_times):
        env.add_vehicle(f'Truck {i+1}', arrival_time, 'Truck', route)

    for i, arrival_time in enumerate(car_arrival_times):
        env.add_vehicle(f'Car {i+1}', arrival_time, 'Car', route)

    env.env.run(until=block_end_sec + 7200)

    return env

def get_video_links(block, in_out_route):
  videos_dictionary_routes = {'Insulfoam-Insulfoam':'https://youtu.be/3KzU9KRVoWI',
                              'Insulfoam-Military':'https://youtu.be/UkLgMqMTxZg',
                              'Military-Insulfoam':'https://youtu.be/_yHpdqUcARc',
                              'Military-Military':'https://youtu.be/cBokCHM10Wk',
                              'Marathon-Military':'https://youtu.be/mUyvtxAP4zw',
                              'Military-Marathon':'https://youtu.be/HtfOFxKr_B8',
                              'Marathon-Marathon':'https://youtu.be/eHKcqA9KRTs',
                              'ABI-Military':'https://youtu.be/nHuN5t2B9fI',
                              'Military-ABI':'https://youtu.be/MhmopqJD3FM',
                              'ABI-ABI':'https://youtu.be/xDGJrYZeUCk',
                              'ABI-Roger':'Situation Not Possible',
                              'Roger-ABI':'https://youtu.be/Ztc7qL2tz5c',
                              'Roger-Roger':'Situation Not Possible',
                              'Roger-Transit':'https://youtu.be/0_5laDRaC_8',
                              'Transit-Transit':'https://youtu.be/6fjrdVjUCFw',
                              'ABI-PetroStar':'https://youtu.be/-6q3lxSxhiA',
                              'Marathon-PetroStar':'https://youtu.be/Jpmh-XndfuE',
                              'PetroStar-ABI':'https://youtu.be/fIQPxQiyxJs',
                              'Tidewater-Tidewater':'https://youtu.be/br55TbzjZAU',
                              'Track J-Track J':'https://youtu.be/OczCBPOJxtY',
                              'Track J-Insulfoam':'https://youtu.be/3YeQW0h056I',
                              'Insulfoam-Track J':'https://youtu.be/Cm63Ogw-FxA',
                              'Track J-Marathon':'https://youtu.be/Wi1LbmD5LEU',
                              'Marathon-Track J':'https://youtu.be/mCzottnXMEo',
                              'Track J-ABI':'https://youtu.be/uJHPqry7MpQ',
                              'ABI-Track J':'https://youtu.be/dskH4hbyeq0',
                              'ABI-Marathon':'https://youtu.be/YepY9-EfHOI',
                              'Marathon-ABI':'https://youtu.be/qLtuyER5cqg'
                              }
  videos_dictionary_sections = {'Construction at Crossing Before Checkpoint':'https://youtu.be/xgwq3Pz9r2Y',
                                'Construction at Ocean Dock Rd and Roger Graves Rd':'https://youtu.be/mGFiOK9nf_Q',
                                'Anchorage Port Rd':'Stoppage?',
                                'Terminal Rd':'https://youtu.be/wZoqDZwhaYI',
                                'Section 1':'https://youtu.be/ZzP9m2a6tu8',
                                'Section 2':'https://youtu.be/sf7Z7N8GeZo',
                                'Section 3':'https://youtu.be/FX6_zELGAw4',
                                'Section 4':'https://youtu.be/WurVYVKAOjo',
                                'Section 5':'https://youtu.be/_XmFWDPR7B8',
                                'Section 6':'https://youtu.be/0rZ8zQWG7IE',
                                'Section 7':'https://youtu.be/4TygqOW-lwQ',
                                'Section 8':'https://youtu.be/lT-6GukIviA'
                              }

  video_while_running = videos_dictionary_sections.get(block)
  video_after_running = videos_dictionary_routes.get(in_out_route)
  return video_while_running, video_after_running


class SimulationPlotter:
    def __init__(self, env, dpi=100, image_width_px=1024, image_height_px=768):
        self.env = env
        self.dpi = dpi
        self.width_inch = image_width_px / dpi
        self.height_inch = image_height_px / dpi


    def plot_histograms(self):
        
        root_path = os.environ.get('BASE_PATH')

        # Adjust the order of data and labels to match the requested sequence
        data_waiting = [self.env.global_waiting_times_normal, self.env.global_waiting_times_taking_detour, self.env.global_waiting_times_no_reaction]
        labels_waiting = ['Normal Operation', 'Taking Detour', 'No Reaction']

        # Save data to JSON before plotting
        waiting_data = root_path + "/scenarioanalysis/data/waiting_data_short.json"
        self.save_data_to_json(data_waiting, labels_waiting, waiting_data)

        plt.figure(figsize=(self.width_inch, self.height_inch), dpi=self.dpi)
        plt.boxplot(data_waiting, labels=labels_waiting)
        plt.title('Comparison of Waiting Times Under Different Conditions')
        plt.ylabel('Waiting Time (seconds)')
        plt.grid(True)
        plt.tight_layout()
        plt.show()  # Display the waiting time comparison plot


        data_cycle = [self.env.global_cycle_times_normal, self.env.global_cycle_times_taking_detour, self.env.global_cycle_times_no_reaction]
        labels_cycle = ['Normal Operation', 'Taking Detour', 'No Reaction']

        # Save cycle time data to JSON

        cycle_data = root_path + "/scenarioanalysis/data/cycle_data_short.json"
        self.save_data_to_json(data_cycle, labels_cycle, cycle_data)

        plt.figure(figsize=(self.width_inch, self.height_inch), dpi=self.dpi)
        plt.boxplot(data_cycle, labels=labels_cycle)
        plt.title('Comparison of Cycle Times Under Different Conditions')
        plt.ylabel('Cycle Time (seconds)')
        plt.grid(True)
        plt.tight_layout()
        plt.show()  # Display the cycle time comparison plot

    def save_data_to_json(self, data, labels, filename):
        data_dict = {label: [int(x) if isinstance(x, np.integer) else x for x in times] for label, times in zip(labels, data)}
        with open(filename, 'w') as file:
            json.dump(data_dict, file, indent=4)


def get_routes_for_block(segment):
    # Dictionary mapping block segments to their respective routes
    routes = {
        'Section 1': [
            'Insulfoam-Insulfoam',
            'Insulfoam-Military',
            'Military-Insulfoam',
            'Military-Military'
        ],
        'Section 2': [
            'Marathon-Military',
            'Marathon-Marathon',
            'Military-Marathon',
            'Military-Military',
            'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid'
        ],
        'Section 3': [
            'ABI-Military',
            'Military-ABI',
            'ABI-ABI',
            'Military-Military',
            'Marathon Transit Area Hybrid-Military',
            'Military-Marathon Transit Area Hybrid'
        ],
        'Section 4': [
            'ABI-Roger',
            'Roger-ABI',
            'ABI-ABI',
            'Roger-Roger',
            'ABI-Military',
            'Roger-Transit'
        ],
        'Section 5': [
            'Roger-Transit',
            'Transit-Transit',
            'Roger-Roger'
        ],
        'Section 6': [
            'Transit-Transit'
        ],
        'Section 7': [
            'ABI-PetroStar',
            'PetroStar-ABI',
            'PetroStar-PetroStar',
            'ABI-ABI'
        ],
        'Section 8': [
            'Tidewater-Tidewater',
            'Marathon Transit Area Hybrid-Marathon Transit Area Hybrid',
            'ABI-ABI',
            'Track J-Track J'
        ],
        'Section 9': ['Tidewater-Tidewater']
    }
    return routes.get(segment, [])

def compare_routes(excel_file_trucks, excel_file_cars, block_location, in_out_route, block_duration_type, block_date, block_hour, reaction_time):
    results = []
    possible_routes = get_routes_for_block(block_location)

    for route in possible_routes:
        obj = setup_simulation(excel_file_trucks, excel_file_cars, block_location, in_out_route, block_duration_type, block_date, block_hour, reaction_time)
        avg_waiting_normal = np.round(np.mean(obj.global_waiting_times_normal) if obj.global_waiting_times_normal else 0)
        avg_waiting_no_reaction = np.round(np.mean(obj.global_waiting_times_no_reaction) if obj.global_waiting_times_no_reaction else 0)
        avg_waiting_taking_detour = np.round(np.mean(obj.global_waiting_times_taking_detour) if obj.global_waiting_times_taking_detour else 0)

        avg_cycle_normal = np.round(np.mean(obj.global_cycle_times_normal) if obj.global_cycle_times_normal else 0)
        avg_cycle_no_reaction = np.round(np.mean(obj.global_cycle_times_no_reaction) if obj.global_cycle_times_no_reaction else 0)
        avg_cycle_taking_detour = np.round(np.mean(obj.global_cycle_times_taking_detour) if obj.global_cycle_times_taking_detour else 0)

        results.append({
            'Route': route,
            'Average Waiting Time - Normal': avg_waiting_normal,
            'Average Waiting Time - No Reaction': avg_waiting_no_reaction,
            'Average Waiting Time - Taking Detour': avg_waiting_taking_detour,
            'Average Cycle Time - Normal': avg_cycle_normal,
            'Average Cycle Time - No Reaction': avg_cycle_no_reaction,
            'Average Cycle Time - Taking Detour': avg_cycle_taking_detour
        })

    results_df = pd.DataFrame(results)
    return results_df

    if current_results:
        for col in ['Average Waiting Time Before', 'Average Waiting Time After', 'Average Cycle Time Before', 'Average Cycle Time After']:
            diff_col_name = 'Diff ' + col
            results_df[diff_col_name] = results_df[col] - current_results[col]

    return results_df


def main_execution(excel_file_trucks, excel_file_cars, block_location, in_out_route, block_duration_type, block_date, block_hour, reaction_time):
    root_path = os.environ.get('BASE_PATH')
    video_while_running, video_after_running = get_video_links(block_location, in_out_route)
    print('The link to the video to play while the code is running:', video_while_running)
    print('The link to the video to play after the results come out:', video_after_running)


    # Run the simulation setup with modified parameters
    env = setup_simulation(excel_file_trucks, excel_file_cars, block_location, in_out_route, block_duration_type, block_date, block_hour, reaction_time)

    # Plotting simulation histograms
    plotter = SimulationPlotter(env)
    plotter.plot_histograms()
    results_df = compare_routes(excel_file_trucks, excel_file_cars, block_location, in_out_route, block_duration_type, block_date, block_hour, reaction_time)

    # Convert the DataFrame to a JSON string
    results_json = results_df.to_json(orient="records", indent=4)

    # Specify the path and filename for the JSON file you want to save
    
    results_json_path = root_path + "/scenarioanalysis/data/simulation_results_short.json"

    # Write the JSON string to a file
    with open(results_json_path, 'w') as file:
        file.write(results_json)