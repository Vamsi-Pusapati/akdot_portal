#Main Code
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import simpy
import random
import os

class TrafficDataProcessor:
    def __init__(self, excel_file, block_start_date, block_end_date):
        self.excel_file = excel_file
        self.block_start_date = datetime.strptime(block_start_date, '%d %b %Y')
        self.block_end_date = datetime.strptime(block_end_date, '%d %b %Y')
        self.monthly_tables = self.load_data()
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def load_data(self):
        """Load and process data from the Excel file using the new dataset format."""
        monthly_tables = {}
        with pd.ExcelFile(self.excel_file) as xls:
            for sheet_name in xls.sheet_names:
                try:
                    df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                    month, year = self.parse_sheet_name(sheet_name)
                    processed_data = self.process_sheet_data(df, month, year)
                    monthly_tables[sheet_name] = processed_data
                except ValueError as e:
                    print(f"Error processing '{sheet_name}': {e}")
        return monthly_tables

    @staticmethod
    def parse_sheet_name(sheet_name):
        """Parse the sheet name to extract the month and year."""
        month, year = sheet_name.strip().split('-')
        year = int(year.strip())
        month = datetime.strptime(month.strip(), '%b').month
        return month, year

    def process_sheet_data(self, df, month, year):
        """Process each sheet's data according to the original data processing method."""
        days_in_month = calendar.monthrange(year, month)[1]
        processed_data = np.full((24, days_in_month), -1, dtype=int)  # Initialize with -1 for missing values

        start_day_of_week = datetime(year, month, 1).weekday()
        for day in range(1, days_in_month + 1):
            for hour in range(df.shape[0]):
                if day-1 < df.shape[1]:
                    value = df.iloc[hour, day-1]
                    if pd.notna(value) and value != -1:
                        processed_data[hour, day-1] = value
        return processed_data

    def calculate_averages(self):
        """Calculate average arrivals for each month, day of week, and hour."""
        averages = {}
        for sheet_name, month_data in self.monthly_tables.items():
            month, year = self.parse_sheet_name(sheet_name)
            start_day_of_month = datetime(year, month, 1).weekday()

            num_days = month_data.shape[1]
            for day in range(num_days):
                day_name = self.days[(start_day_of_month + day) % 7]
                for hour in range(24):
                    value = month_data[hour, day]
                    if value != -1:
                        key = (month, day_name, hour)  # Updated key to include month
                        if key not in averages:
                            averages[key] = {'sum': 0, 'count': 0}
                        averages[key]['sum'] += value
                        averages[key]['count'] += 1

        # Calculate the final averages
        for key in averages.keys():
            averages[key] = averages[key]['sum'] / averages[key]['count']

        return averages

    def create_arrival_schedule(self):
            averages = self.calculate_averages()

            arrival_schedule_seconds = []
            current_date = self.block_start_date

            while current_date <= self.block_end_date:
                month = current_date.month
                day_of_week_name = current_date.strftime('%A')

                for hour in range(24):
                    key = (month, day_of_week_name, hour)
                    average_arrivals = averages.get(key, 0)

                    # Generate arrival times using Poisson distribution for the number of arrivals
                    num_arrivals = np.random.poisson(average_arrivals)

                    # For each arrival, generate a random second within the hour
                    for _ in range(num_arrivals):
                        second = np.random.randint(0, 3600)  # Random second within the hour
                        arrival_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(seconds=second)
                        seconds_since_start = (arrival_time - self.block_start_date).total_seconds()
                        arrival_schedule_seconds.append(seconds_since_start)

                current_date += timedelta(days=1)

            # Optionally, sort the schedule if exact order is important
            arrival_schedule_seconds.sort()

            return sorted(arrival_schedule_seconds)


class Train:
    def __init__(self, start_date_str, end_date_str):
        self.start_date = datetime.strptime(start_date_str, '%d %b %Y')
        self.end_date = datetime.strptime(end_date_str, '%d %b %Y')
        self.train_block_schedule = self.generate_station_times()

    def generate_station_times(self):
        schedule = []
        days_of_simulation = (self.end_date - self.start_date).days + 1
        for days_from_start in range(days_of_simulation):
            num_blocks = random.randint(0, 1)  # Number of blocks for the day
            for _ in range(num_blocks):
                hour_block = random.randint(6, 17)  # Hour between 6 to 17
                minute_block = random.randint(0, 59)  # Minute between 0 to 59
                duration = random.randint(120, 600)  # Duration in seconds
                start_second = days_from_start * 86400 + hour_block * 3600 + minute_block * 60
                end_second = start_second + duration
                schedule.append((start_second, end_second))
        return schedule

    def is_in_station(self, current_time):
        # Check if the current simulation second is within any block interval
        for start_second, end_second in self.train_block_schedule:
            if start_second <= current_time < end_second:
                return True
        return False


class Vehicle:
    def __init__(self, environment, name, vehicle_type, check_in, track_j_gate, waiting_times, cycle_times, hazmat_waits, num_of_vehicles, num_of_trucks, num_of_hazmat, hazmat_lane, block, train, route_distribution):
        self.env = environment.sim_env
        self.environment = environment
        self.name = name
        self.vehicle_type = vehicle_type
        self.check_in = check_in
        self.track_j_gate = track_j_gate
        self.waiting_times = waiting_times
        self.cycle_times = cycle_times
        self.hazmat_waits = hazmat_waits
        self.num_of_vehicles = num_of_vehicles
        self.num_of_trucks = num_of_trucks
        self.num_of_hazmat = num_of_hazmat
        self.hazmat_lane = hazmat_lane
        self.route_distribution = route_distribution
        self.block = block
        self.train = train

        self.set_alternate_routes(block)
        self.route_to, self.route_from = self.select_route_based_on_condition()


    def set_alternate_routes(self, block):
        if block == 'Construction at Crossing Before Checkpoint':
            #'Track J','Insulfoam'

            self.route_to_matson_option1 = ['Second Fork to Matson','First Fork to Second Fork', 'Gate to First Fork','Insulfoam to Gate']
            self.route_to_tote_option1 = ['Second Fork to Tote','First Fork to Second Fork','Gate to First Fork', 'Insulfoam to Gate']
            self.route_from_matson_option1 = ['Track J', 'Track J to Matson']
            self.route_from_tote_option1 = ['Track J', 'Track J to Tote']

            #'Track J','Track J'
            self.route_to_matson_option2 = ['Track J', 'Track J to Matson']
            self.route_to_tote_option2 = ['Track J', 'Track J to Tote']
            self.route_from_matson_option2 = ['Track J to Matson', 'Track J']
            self.route_from_tote_option2 = ['Track J to Tote', 'Track J']

        elif block == 'Construction at Ocean Dock Rd and Roger Graves Rd':
            #'Marathon','Track J'
            self.route_to_matson_option1 = ['Marathon', 'First Fork to Second Fork', 'Second Fork to Matson']
            self.route_to_tote_option1 = ['Marathon', 'First Fork to Second Fork', 'Second Fork to Tote']
            self.route_from_matson_option1 = ['Track J to Matson', 'Track J']
            self.route_from_tote_option1 = ['Track J to Tote', 'Track J']

            #'Track J','Track J'
            self.route_to_matson_option2 = ['Track J', 'Track J to Matson']
            self.route_to_tote_option2 = ['Track J', 'Track J to Tote']
            self.route_from_matson_option2 = ['Track J to Matson', 'Track J']
            self.route_from_tote_option2 = ['Track J to Tote', 'Track J']

        elif block == 'Anchorage Port Rd':
            #'ABI','Transit A'
            self.route_to_matson_option1 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Matson ABI']
            self.route_to_tote_option1 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork through ABI', 'Second Fork to Tote']
            self.route_from_matson_option1 = ['Matson to First Fork through Transt A', 'Gate to First Fork', 'Ocean to Gate']
            self.route_from_tote_option1 = ['Tote to First Fork through Transt A', 'Gate to First Fork', 'Ocean to Gate']

            #'Track J','Track J'
            self.route_to_matson_option2 = ['Track J', 'Track J to Matson']
            self.route_to_tote_option2 = ['Track J', 'Track J to Tote']
            self.route_from_matson_option2 = ['Track J to Matson', 'Track J']
            self.route_from_tote_option2 = ['Track J to Tote', 'Track J']

        elif block == 'Terminal Rd':
            #'Transit A','Transit A'
            self.route_to_matson_option1 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Matson']
            self.route_to_tote_option1 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Tote to Second Fork through Transit A']
            self.route_from_matson_option1 = ['Second Fork to Matson', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']
            self.route_from_tote_option1 = ['Tote to Second Fork through Transit A', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']

            self.route_to_matson_option2 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Matson']
            self.route_to_tote_option2 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Tote to Second Fork through Transit A']
            self.route_from_matson_option2 = ['Second Fork to Matson', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']
            self.route_from_tote_option2 = ['Tote to Second Fork through Transit A', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']

        elif block == 'None':
            self.route_to_matson_option1 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Matson']
            self.route_to_tote_option1 = ['Second Fork to Matson', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']
            self.route_from_matson_option1 = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Tote']
            self.route_from_tote_option1 = ['Second Fork to Tote', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']


    def select_route_based_on_condition(self):
        destination = random.choice(['Matson', 'Tote'])
        distribution = self.route_distribution[self.block]
        choice = random.choices(population=[0, 1], weights=distribution, k=1)[0]

        if choice == 0:
            route_to = self.route_to_matson_option1 if destination == 'Matson' else self.route_to_tote_option1
            route_from = self.route_from_matson_option1 if destination == 'Matson' else self.route_from_tote_option1
        else:
            route_to = self.route_to_matson_option2 if destination == 'Matson' else self.route_to_tote_option2
            route_from = self.route_from_matson_option2 if destination == 'Matson' else self.route_from_tote_option2


        return route_to, route_from


    def transportation_time(self, route):
        # Map of standard travel times for each part of the route
        standard_travel_times = {
            'Marathon': 0.6*3600/15,
            'Ocean to Gate': 0.26 * 3600 / 20,
            'Insulfoam to Gate': 0.37 * 3600 / 15,
            'Gate to First Fork': 0.18 * 3600 / 20,
            'First Fork to Second Fork': 0.14 * 3600 / 20,
            'First Fork to Matson ABI': 0.60 * 3600 / 10,
            'First Fork to Matson Sement Dock': 0.65 * 3600 / 10,
            'First Fork to Second Fork through ABI': 0.50 * 3600 / 15,
            'Tote to First Fork through Transt A': 1.8 * 3600 / 20,
            'Tote to Second Fork through Transit A': 0.6 * 3600 /15,
            'Second Fork to Matson': 0.4 * 3600 / 20,
            'Second Fork to Tote': 0.7 * 3600 / 20,
            'Track J': 0.5 * 3600 / 10,
            'Track J to Tote': 0.7 * 3600 / 20,
            'Track J to Matson': 0.45 * 3600 / 20}

        # Calculating the standard time for the entire route
        time = sum(standard_travel_times.get(street, 0) for street in route)

        # Calculate the current simulation time and convert to day and month
        simulation_second = int(self.env.now)
        current_date = self.environment.start_date + timedelta(seconds=simulation_second)
        month = current_date.month
        hour = current_date.hour
        is_night = 19 <= hour or hour <= 7

        # Time adjustment factors based on the month
        month_time_factors = {
            1: 1.10, 2: 1.10, 3: 1.05, 4: 1.00,
            5: 0.90, 6: 0.80, 7: 0.80, 8: 0.80,
            9: 0.90, 10: 1.00, 11: 1.05, 12: 1.10}

        # Adjusting time based on the month and night conditions
        time *= month_time_factors.get(month, 1)
        if is_night:
            time *= 1.05

        # Returning the calculated time
        return time


    def run(self, arrival_time):
        yield self.env.timeout(arrival_time)
        #print(f"{self.name} arrived at {self.env.now}")

        arrival_seconds = int(self.env.now)  # Convert numpy.int64 to Python int
        current_datetime = self.environment.start_date + timedelta(seconds=arrival_seconds)


        # Define 'day' and 'hour' based on the current simulation time
        day = current_datetime.weekday()  # 0: Monday, 1: Tuesday, ... 6: Sunday
        hour = current_datetime.hour

        # Check the first segment and use the appropriate gate
        first_segment = self.route_to[0]
        if first_segment == 'Track J':
            with self.track_j_gate.request() as track_j_request:
                yield track_j_request
                at_the_gate = self.env.now
                self.environment.track_j_counter += 1
                yield self.env.timeout(np.round(random.randint(10,20)))
                enter_the_port = self.env.now
        else:
            with self.check_in.request() as check_in_request:
                yield check_in_request
                at_the_gate = self.env.now
                self.environment.check_in_counter += 1
                yield self.env.timeout(np.round(random.randint(10,20)))
                enter_the_port = self.env.now

            block_time = 0

            # Now, when adding block_time as a timedelta, it makes sense
            while self.train.is_in_station(enter_the_port + block_time):
                block_time += 1

            yield self.env.timeout(block_time)

            enter_the_port = self.env.now

        #Compute Travel Time

        gate_to_station_time = self.transportation_time(self.route_to)
        yield self.env.timeout(gate_to_station_time)


        # Logic for processing at the destination for Trucks
        if self.vehicle_type == 'Truck':
            enter_containeryard_time = self.env.now

            time_ranges = [(600, 750), (500, 600), (900, 1200)]
            probabilities = [0.5, 0.3, 0.2]

            selected_range = random.choices(time_ranges, probabilities, k=1)[0]

            unloading_loading = random.randint(selected_range[0], selected_range[1])

            yield self.env.timeout(unloading_loading)
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
                    self.hazmat_waits[day][hour].append(hazmat_wait)
                    self.num_of_hazmat[day][hour] +=1

            # Maintenance if required
            if random.random() < 0.1:
                maintenance_process = random.randint(600, 900)
                yield self.env.timeout(maintenance_process)


        # Process the route from the destination
        yield self.env.timeout(self.transportation_time(self.route_from))

        # Calculate waiting and cycle times
        waiting_time = enter_the_port - arrival_time
        cycle_time = self.env.now - arrival_time


        self.waiting_times[day][hour].append(waiting_time)
        if self.vehicle_type == 'Truck':
            self.cycle_times[day][hour].append(cycle_time)


class Environment:
    def __init__(self, block, route_distribution, start_date_str, end_date_str):
        self.sim_env = simpy.Environment()
        self.check_in = simpy.Resource(self.sim_env, capacity=1)
        self.track_j_gate = simpy.Resource(self.sim_env, capacity=1)
        self.hazmat_lane = simpy.Resource(self.sim_env, capacity=1)
        self.route_distribution = route_distribution
        self.block = block
        self.start_date = datetime.strptime(start_date_str, '%d %b %Y')
        self.end_date = datetime.strptime(end_date_str, '%d %b %Y')
        self.train = Train(start_date_str, end_date_str)
        self.cycle_times = {day: {hour: [] for hour in range(24)} for day in range(7)}
        self.waiting_times = {day: {hour: [] for hour in range(24)} for day in range(7)}
        self.hazmat_waits = {day: {hour: [] for hour in range(24)} for day in range(7)}
        self.num_of_vehicles = {day: {hour: 0 for hour in range(24)} for day in range(7)}
        self.num_of_trucks = {day: {hour: 0 for hour in range(24)} for day in range(7)}
        self.num_of_hazmat = {day: {hour: 0 for hour in range(24)} for day in range(7)}
        self.track_j_counter = 0
        self.check_in_counter = 0


    def add_vehicle(self, name, arrival_time, vehicle_type):
        # Convert arrival time to actual date and time based on the start date
        arrival_datetime = self.start_date + timedelta(seconds=int(arrival_time))
        day_of_week = arrival_datetime.weekday()  # 0: Monday, 1: Tuesday, ... 6: Sunday
        hour = arrival_datetime.hour

        # Increment the vehicle count based on the day of the week and hour
        self.num_of_vehicles[day_of_week][hour] += 1
        if vehicle_type == 'Truck':
            self.num_of_trucks[day_of_week][hour] += 1

        vehicle = Vehicle(self, name, vehicle_type, self.check_in, self.track_j_gate, self.waiting_times,
                          self.cycle_times, self.hazmat_waits, self.num_of_vehicles, self.num_of_trucks,
                          self.num_of_hazmat, self.hazmat_lane, self.block, self.train, self.route_distribution)
        self.sim_env.process(vehicle.run(arrival_time))

def setup_simulation(filtered_truck_schedule, filtered_car_schedule, block, route_distribution, start_date, end_date):
    env = Environment(block, route_distribution, start_date, end_date)

    for i, arrival_time in enumerate(filtered_truck_schedule):
        env.add_vehicle(f'Truck {i+1}', arrival_time, 'Truck')
    for i, arrival_time in enumerate(filtered_car_schedule):
        env.add_vehicle(f'Car {i+1}', arrival_time, 'Car')

    env.sim_env.run(until=max(filtered_truck_schedule[-1], filtered_car_schedule[-1]))

    return env

class TimeDataPlotter:
    def __init__(self, env, dpi=100, image_width_px=512, image_height_px=248):
        self.env = env
        self.dpi = dpi
        self.width_inch = image_width_px / dpi
        self.height_inch = image_height_px / dpi
        self.day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    def save_data_as_json(self, time_data, title, y_label, file_name, replace_zeros=True, convert_to_minutes=False, aggregation_function=np.nanmean):
        root_path = os.environ.get('BASE_PATH')
        days = list(time_data.keys())
        hours = list(time_data[days[0]].keys())
        data_for_json = {}

        for day in days:
            values = []
            for hour in hours:
                if replace_zeros and time_data != self.env.hazmat_waits:
                    if all(x == 0 for x in time_data[day][hour]):
                        value = 0
                    else:
                        value = aggregation_function(time_data[day][hour])
                else:
                    value = aggregation_function(time_data[day][hour]) if any(time_data[day][hour]) else 0

                if convert_to_minutes:
                    value /= 60

                values.append(value)

            data_for_json[self.day_names[day]] = values
        file_path = root_path + "/scenarioanalysis/data/" + file_name
        with open(file_path, 'w') as f:
            json.dump(data_for_json, f, indent=4)

class TimeDataPlotters:
    def __init__(self, env, dpi=100, image_width_px=512, image_height_px=248):
        self.env = env
        self.dpi = dpi
        self.width_inch = image_width_px / dpi
        self.height_inch = image_height_px / dpi
        self.day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def save_daily_data_as_json(self, time_data, title_template, y_label, file_name_template):
        days = list(time_data.keys())
        hours = list(range(24))  # Assuming the data is provided hourly
        root_path = os.environ.get('BASE_PATH')
        data_path = root_path + "/scenarioanalysis/data/"
        for day in days:
            day_values = [np.mean(time_data[day][hour]) if time_data[day][hour] else 0 for hour in hours]
            data_for_json = {self.day_names[day]: day_values}
            file_name = file_name_template.format(self.day_names[day])
            file_path = data_path + file_name
            with open(file_path, 'w') as f:
                json.dump(data_for_json, f, indent=4)


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
  video_after_running = videos_dictionary_routes.get(block)
  return video_while_running, video_after_running

# Function to calculate average and maximum waiting and cycle times
def calculate_aggregated_metrics(env):
    # Calculate average and maximum for waiting times
    avg_waiting_time = np.mean([np.mean(times) for day in env.waiting_times.values() for hour, times in day.items() if times])
    max_waiting_time = np.max([np.max(times) for day in env.waiting_times.values() for hour, times in day.items() if times])

    # Calculate average and maximum for cycle times
    avg_cycle_time = np.mean([np.mean(times) for day in env.cycle_times.values() for hour, times in day.items() if times])
    max_cycle_time = np.max([np.max(times) for day in env.cycle_times.values() for hour, times in day.items() if times])

    return avg_waiting_time, max_waiting_time, avg_cycle_time, max_cycle_time

# Function to run simulation with different route distributions and save results
def run_simulation_for_distributions(car_excel_file, truck_excel_file, start_date, end_date, block, route_distribution):
    results = []
    for distribution in distributions:
        route_distribution = {block: distribution}
        # Run the simulation here using the specified route_distribution
        env = run_simulation(car_excel_file, truck_excel_file, start_date, end_date, block, route_distribution)
        avg_waiting_time, max_waiting_time, avg_cycle_time, max_cycle_time = calculate_aggregated_metrics(env)

        results.append({
            'Distribution': str(distribution),
            'Average Waiting Time (sec)': np.round(avg_waiting_time),
            'Maximum Waiting Time (sec)': np.round(max_waiting_time),
            'Average Cycle Time (min)': np.round(avg_cycle_time/60,1),
            'Maximum Cycle Time (min)': np.round(max_cycle_time/60,1)
        })

    return pd.DataFrame(results)

# Route distribution values to run
distributions = [
    [0, 1],
    [0.25, 0.75],
    [0.5, 0.5],
    [0.75, 0.25],
    [1, 0]
]


def run_simulation(car_excel_file, truck_excel_file, start_date_str, end_date_str, block, route_distribution):
    # Initialize the TrafficDataProcessor for trucks and cars
    truck_processor = TrafficDataProcessor(truck_excel_file, start_date_str, end_date_str)
    car_processor = TrafficDataProcessor(car_excel_file, start_date_str, end_date_str)

    # Create arrival schedules for trucks and cars
    truck_arrival_schedule = truck_processor.create_arrival_schedule()
    car_arrival_schedule = car_processor.create_arrival_schedule()

    # Setup and run the simulation
    env = setup_simulation(truck_arrival_schedule, car_arrival_schedule, block, route_distribution, start_date_str, end_date_str)

    return env  # Return the environment object for further use


def execute_simulation_and_plotting(car_excel_file, truck_excel_file, start_date_str, end_date_str, block, route_distribution):
    # Video links for while the code is running and after the results
    video_while_running, video_after_running = get_video_links(block, block)
    print('The link to the video to play while the code is running:', video_while_running)
    print('The link to the video to play after the results come out:', video_after_running)

    # Run the initial simulation
    env = run_simulation(car_excel_file, truck_excel_file, start_date_str, end_date_str, block, route_distribution)

    # Assuming 'env' is your environment object from the simulation
    num_trucks_per_hour = env.num_of_trucks  # Extracting the number of trucks data
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours_of_day = list(range(24))

    # Create a JSON data structure instead of plotting
    truck_data = {}
    for day in range(7):
        truck_data_per_hour = [num_trucks_per_hour[day][hour] for hour in hours_of_day]
        truck_data[days_of_week[day]] = truck_data_per_hour

    root_path = os.environ.get('BASE_PATH')
    truck_data = root_path + "/scenarioanalysis/data/truck_data_long.json"

    with open(truck_data, 'w') as json_file:
        json.dump(truck_data, json_file, indent=4)

    # Instantiate plotter classes
    plotter = TimeDataPlotter(env)

    # Saving data as JSON instead of plotting
    plotter.save_data_as_json(env.waiting_times, 'Average Waiting Time per Day-Hour', 'Seconds', 'average_waiting_times_long.json')
    plotter.save_data_as_json(env.cycle_times, 'Average Cycle Time per Day-Hour', 'Minutes', 'average_cycle_times_long.json', convert_to_minutes=True)
    plotter.save_data_as_json(env.hazmat_waits, 'Average Hazmat Wait Time per Day-Hour', 'Seconds', 'hazmat_wait_times_long.json', replace_zeros=False)

    # Optionally run simulations for different route distributions and save results
    results_df = run_simulation_for_distributions(car_excel_file, truck_excel_file, start_date_str, end_date_str, block, route_distribution)

    # Save results_df to a JSON file
    
    root_path = os.environ.get('BASE_PATH')
    data_path = root_path + "/scenarioanalysis/data/"
    save_path_json = data_path + "simulation_results_long.json"

    results_df.to_json(save_path_json, orient='records', indent=4)

    return results_df