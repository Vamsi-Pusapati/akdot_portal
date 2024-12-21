import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import calendar
from datetime import datetime, timedelta
import simpy
import random
import json
import os

class TrafficDataProcessor:
    def __init__(self, excel_file,today_date):
        self.excel_file = excel_file
        self.today_date = today_date
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.data = self.load_and_process_data()
        self.arrival_schedule = self.create_arrival_schedule_for_current_month()

    def load_and_process_data(self):
        sheet_names = pd.ExcelFile(self.excel_file).sheet_names
        processed_data = {}
        for sheet_name in sheet_names:
            try:
                month, year = sheet_name.split('-')
                month = month.strip()
                year = int(year.strip())
                start_day_of_week = datetime(year, datetime.strptime(month, '%b').month, 1).weekday()
                days_in_month = pd.Period(sheet_name).days_in_month
            except ValueError as e:
                print(f"Error parsing sheet name '{sheet_name}': {e}. Skipping this sheet.")
                continue

            df = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
            self.process_sheet_data(df, start_day_of_week, month, year, processed_data, days_in_month)
        return processed_data

    def process_sheet_data(self, df, start_day_of_week, month, year, processed_data, days_in_month):
        for day in range(1, days_in_month + 1):
            day_of_week = self.days[(start_day_of_week + day - 1) % 7]
            for hour in range(df.shape[0]):
                value = df.iloc[hour, day-1] if day-1 < df.shape[1] else np.nan
                if pd.notna(value) and value != -1:
                    key = (month, day_of_week, hour)
                    processed_data.setdefault(key, []).append(value)

    def arrival_params(self, month, day_of_week, hour):
        key = (month, day_of_week, hour)
        if key in self.data:
            values = self.data[key]
            mean = np.mean(values)
            variance = np.var(values)
            return mean, variance
        return None, None

    def calculate_weekly_arrival_stats(self):
        month_name = self.today_date.strftime('%b')
        self.weekly_stats = {day: {'mean': [], 'variance': []} for day in self.days}

        for day in self.days:
            daily_mean = []
            daily_variance = []
            for hour in range(24):  # Assuming data is available for each hour
                mean, variance = self.arrival_params(month_name, day, hour)
                if mean is not None and variance is not None:
                    daily_mean.append(mean)
                    daily_variance.append(variance)

            if daily_mean and daily_variance:
                self.weekly_stats[day]['mean'] = np.sum(daily_mean)
                self.weekly_stats[day]['variance'] = np.sum(daily_variance)


    def plot_weekly_arrival_stats_and_save_trucks(self):
        days = list(self.weekly_stats.keys())
        plt.figure(figsize=(10, 6))

        for i, day in enumerate(days, start=1):
            mean = self.weekly_stats[day]['mean']
            std_dev = np.sqrt(self.weekly_stats[day]['variance'])
            lower_bound = mean - std_dev
            upper_bound = mean + std_dev

        # Preparing data for JSON
        data_for_json = self.weekly_stats

        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        # Saving the data as JSON
        json_filename = dashboard_path + 'weekly_counts_trucks.json'
        with open(json_filename, 'w') as json_file:
            json.dump(data_for_json, json_file, indent=4)

        # Returning the paths to the saved files for your reference
        return json_filename

    def plot_weekly_arrival_stats_and_save_cars(self):
        days = list(self.weekly_stats.keys())
        plt.figure(figsize=(10, 6))

        for i, day in enumerate(days, start=1):
            mean = self.weekly_stats[day]['mean']
            std_dev = np.sqrt(self.weekly_stats[day]['variance'])
            lower_bound = mean - std_dev
            upper_bound = mean + std_dev

        # Preparing data for JSON
        data_for_json = self.weekly_stats

        # Saving the data as JSON
        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_filename = dashboard_path+'weekly_counts_cars.json'
        with open(json_filename, 'w') as json_file:
            json.dump(data_for_json, json_file, indent=4)

        # Returning the paths to the saved files for your reference
        return json_filename


    def create_arrival_schedule_for_current_month(self, mode='mean'):
        first_day_of_current_month = self.today_date.replace(day=1)
        current_month_name = first_day_of_current_month.strftime('%b')
        days_in_month = pd.Period(first_day_of_current_month.strftime('%Y-%m')).days_in_month

        arrival_schedule = []
        for day in range(1, days_in_month + 1):
            current_date = first_day_of_current_month + timedelta(days=day-1)
            day_of_week = self.days[current_date.weekday()]
            for hour in range(24):
                mean, variance = self.arrival_params(current_month_name, day_of_week, hour)
                if mean is not None and variance is not None:
                    std_dev = np.sqrt(variance)
                    if mode == 'mean':
                        num_arrivals = max(0, int(round(mean)))
                    elif mode == 'mean-minus-std':
                        num_arrivals = max(0, int(round(mean - std_dev)))
                    elif mode == 'mean-plus-std':
                        num_arrivals = max(0, int(round(mean + std_dev)))
                    else:
                        raise ValueError("Invalid mode selected. Choose 'mean', 'mean-minus-std', or 'mean-plus-std'.")

                    arrival_seconds = np.sort(np.random.randint(0, 3600, num_arrivals))
                    seconds_from_month_start = ((day-1) * 24 * 3600) + (hour * 3600)
                    adjusted_arrival_times = [seconds_from_month_start + sec for sec in arrival_seconds]
                    arrival_schedule.extend(adjusted_arrival_times)
        return arrival_schedule

class Vehicle:
    def __init__(self, environment, name, arrival_time, vehicle_type, check_in, track_j_gate, Bluff_gate, hazmat_lane, waiting_times,
                 cycle_times, queue_lengths, incoming_distribution, outgoing_distribution, today_date):
        self.env = environment
        self.name = name
        self.arrival_time = arrival_time
        self.today_date = today_date
        self.vehicle_type = vehicle_type
        self.check_in = check_in
        self.track_j_gate = track_j_gate
        self.Bluff_gate = Bluff_gate
        self.hazmat_lane = hazmat_lane
        self.waiting_times = waiting_times
        self.cycle_times = cycle_times
        self.queue_lengths = queue_lengths
        self.incoming_distribution = incoming_distribution
        self.outgoing_distribution = outgoing_distribution
        self.destination = None
        self.entrance_gate = None
        self.exit_gate = None
        self.route_to = None
        self.route_from = None
        self.num_of_hazmat = 0
        self.route_to_matson_main = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Matson']
        self.route_from_matson_main = ['Second Fork to Matson', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']
        self.route_to_tote_main = ['Ocean to Gate', 'Gate to First Fork', 'First Fork to Second Fork', 'Second Fork to Tote']
        self.route_from_tote_main = ['Second Fork to Tote', 'First Fork to Second Fork', 'Gate to First Fork', 'Ocean to Gate']
        self.route_to_matson_Bluff = ['Bluff gate to first fork', 'First Fork to Second Fork', 'Second Fork to Matson']
        self.route_from_matson_Bluff = ['Bluff gate to first fork', 'First Fork to Second Fork', 'Second Fork to Matson']
        self.route_to_tote_Bluff = ['Bluff gate to first fork', 'First Fork to Second Fork', 'Second Fork to Tote']
        self.route_from_tote_Bluff = ['Bluff gate to first fork', 'First Fork to Second Fork', 'Second Fork to Tote']
        self.route_to_matson_track_J = ['Track J', 'Track J to Matson']
        self.route_from_matson_track_J = ['Track J', 'Track J to Tote']
        self.route_to_tote_track_J = ['Track J to Matson', 'Track J']
        self.route_from_tote_track_J = ['Track J to Tote', 'Track J']

    def is_arrival_today(self, seconds_since_start_of_month):
        """Check if the given seconds since start of the month correspond to today's date."""
        # Get today's date and the start of the current month
        start_of_month = self.today_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Convert seconds since start of month to a datetime object
        arrival_date = start_of_month + timedelta(seconds=seconds_since_start_of_month)

        # Check if the arrival date is today
        return arrival_date.date() == self.today_date.date()


    def convert_seconds_to_date_info(self, seconds_since_start_of_month):
        """Convert seconds since start of the month to day of month, day of week, and hour."""
        start_of_month = self.today_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        arrival_date = start_of_month + timedelta(seconds=seconds_since_start_of_month)

        day_of_month = arrival_date.day
        day_of_week = arrival_date.strftime('%A')
        hour = arrival_date.hour

        return day_of_month, day_of_week, hour

    def count_specific_weekday_in_current_month(self,weekday_name):
        start_of_month = self.today_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = start_of_month.replace(month=start_of_month.month % 12 + 1) if start_of_month.month < 12 else start_of_month.replace(year=start_of_month.year + 1, month=1)
        end_of_month = next_month - timedelta(days=1)

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_number = weekdays.index(weekday_name)

        count = 0
        current_day = start_of_month
        while current_day <= end_of_month:
            if current_day.weekday() == weekday_number:
                count += 1
            current_day += timedelta(days=1)

        return count

    def transportation_time(self, route):
        # Map of standard travel times for each part of the route
        standard_travel_times = {
            'Ocean to Gate': 0.26 * 3600 / 20,
            'Insulfoam to Gate': 0.45 * 3600 / 15,
            'Gate to First Fork': 0.18 * 3600 / 20,
            'First Fork to Second Fork': 0.14 * 3600 / 20,
            'First Fork to Second Fork through ABI': 0.54 * 3600 / 15,
            'First Fork to Matson through ABI': 0.65 * 3600 / 10,
            'Tote to Military': 0.6 * 3600 / 20,
            'Roger': 0.2 * 3600 / 15,
            'Roger to Tote': 0.68 * 3600 / 20,
            'Roger to Matson': 0.48 * 3600 / 20,
            'PetroStar': 0.1 * 3600 / 5,
            'PetroStar to Matson': 0.3 * 3600 / 20,
            'Bluff gate to first fork': 0.4 * 3600 / 20,
            'Second Fork to Tote through Transit': 0.71 * 3600 / 15,
            'ABI-Transit Area Hybrid to Matson': 0.7 * 3600 / 15,
            'ABI-Transit Area Hybrid to Tote': 0.7 * 3600 / 15,
            'Matson to Military': 0.67 * 3600 / 20,
            'Marathon to Matson': 1.07 * 3600 / 15,
            'Marathon to second Fork': 0.8 * 3600 / 15,
            'Marathon-Transit Area Hybrid to Matson': 1.2 * 3600 / 15,
            'Marathon-Transit Area Hybrid to Tote': 1.5 * 3600 / 15,
            'First Fork to Tote through Roger Graves Rd': 0.83 * 3600 / 20,
            'Second Fork to Matson': 0.4 * 3600 / 20,
            'Second Fork to Matson theough Tidewater': 0.4 * 3600 / 15,
            'Second Fork to Tote': 0.7 * 3600 / 20}

        # Calculating the standard time for the entire route
        time = sum(standard_travel_times.get(street, 0) for street in route)

        # Calculate the current simulation time and convert to day and month
        simulation_second = int(self.env.simpy_environment.now)
        start_of_month = self.today_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_date = start_of_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(seconds=simulation_second)
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

    def run(self):
        yield self.env.simpy_environment.timeout(self.arrival_time)

        self.arrival_seconds = int(self.env.simpy_environment.now)  # Convert to Python int for compatibility
        self.day_of_month, self.day_of_week, self.hour = self.convert_seconds_to_date_info(self.arrival_seconds)

        if self.vehicle_type == 'Truck':
          # Increment count for the day of the month
          self.env.update_daily_count_trucks(self.day_of_month)

          # Increment count for the day of the week
          self.env.update_weekly_count_trucks(self.day_of_week)

        if self.vehicle_type == 'Car':
          self.env.update_daily_count_cars(self.day_of_month)
          # Increment count for the day of the week
          self.env.update_weekly_count_cars(self.day_of_week)


        # Check if the arrival is today and increment the hourly count if so
        if self.is_arrival_today(self.arrival_seconds) and self.vehicle_type == 'Truck':
            self.env.update_hourly_count_trucks(self.hour)
            # Determine destination randomly: 50% chance for Tote, 50% chance for Matson
            self.destination = 'Tote' if random.random() < 0.5 else 'Matson'

            # Randomly select an entrance gate based on Incoming_distribution
            gates = ['check_in', 'track_j_gate', 'Bluff_gate']
            self.entrance_gate = np.random.choice(gates, p=self.incoming_distribution)
            if self.destination == 'Matson':

              if self.entrance_gate == 'track_j_gate':
                  self.route_to = self.route_to_matson_track_J
                  self.env.update_section_count_trucks('6')
                  self.env.update_section_count_trucks('5')

              elif self.entrance_gate == 'Bluff_gate':
                  self.route_to = self.route_to_matson_Bluff
                  self.env.update_section_count_trucks('7')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('5')

              else:
                  self.route_to = self.route_to_matson_main
                  self.env.update_section_count_trucks('1')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('5')

            if self.destination == 'Tote':

              if self.entrance_gate == 'track_j_gate':
                  self.route_to = self.route_to_tote_track_J
                  self.env.update_section_count_trucks('6')
                  self.env.update_section_count_trucks('4')

              elif self.entrance_gate == 'Bluff_gate':
                  self.route_to = self.route_to_tote_Bluff
                  self.env.update_section_count_trucks('7')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('4')

              else:
                  self.route_to = self.route_to_tote_main
                  self.env.update_section_count_trucks('1')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('4')

            # Randomly select an exit gate based on Outgoing_distribution
            self.exit_gate = np.random.choice(gates, p=self.outgoing_distribution)

            if self.destination == 'Matson':

              if self.exit_gate == 'track_j_gate':
                  self.route_from = self.route_from_matson_track_J
                  self.env.update_section_count_trucks('6')
                  self.env.update_section_count_trucks('5')

              elif self.exit_gate == 'Bluff_gate':
                  self.route_from = self.route_from_matson_Bluff
                  self.env.update_section_count_trucks('7')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('5')

              else:
                  self.route_from = self.route_from_matson_main
                  self.env.update_section_count_trucks('1')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('5')

            if self.destination == 'Tote':

              if self.exit_gate == 'track_j_gate':
                  self.route_from = self.route_from_tote_track_J
                  self.env.update_section_count_trucks('6')
                  self.env.update_section_count_trucks('4')

              elif self.exit_gate == 'Bluff_gate':
                  self.route_from = self.route_from_tote_Bluff
                  self.env.update_section_count_trucks('7')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('4')
              else:
                  self.route_from = self.route_from_matson_main
                  self.env.update_section_count_trucks('1')
                  self.env.update_section_count_trucks('3')
                  self.env.update_section_count_trucks('4')

        if self.is_arrival_today(self.arrival_seconds) and self.vehicle_type == 'Car':
            self.env.update_hourly_count_cars(self.hour)

            # Determine destination randomly: 50% chance for Tote, 50% chance for Matson
            self.destination = 'Tote' if random.random() < 0.5 else 'Matson'

            # Randomly select an entrance gate based on Incoming_distribution
            gates = ['check_in', 'track_j_gate', 'Bluff_gate']
            self.entrance_gate = np.random.choice(gates, p=self.incoming_distribution)
            if self.destination == 'Matson':

              if self.entrance_gate == 'track_j_gate':
                  self.route_to = self.route_to_matson_track_J
                  self.env.update_section_count_cars('6')
                  self.env.update_section_count_cars('5')

              elif self.entrance_gate == 'Bluff_gate':
                  self.route_to = self.route_to_matson_Bluff
                  self.env.update_section_count_cars('7')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('5')

              else:
                  self.route_to = self.route_to_matson_main
                  self.env.update_section_count_cars('1')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('5')

            if self.destination == 'Tote':

              if self.entrance_gate == 'track_j_gate':
                  self.route_to = self.route_to_tote_track_J
                  self.env.update_section_count_cars('6')
                  self.env.update_section_count_cars('4')

              elif self.entrance_gate == 'Bluff_gate':
                  self.route_to = self.route_to_tote_Bluff
                  self.env.update_section_count_cars('7')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('4')

              else:
                  self.route_to = self.route_to_tote_main
                  self.env.update_section_count_cars('1')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('4')

            # Randomly select an exit gate based on Outgoing_distribution
            self.exit_gate = np.random.choice(gates, p=self.outgoing_distribution)

            if self.destination == 'Matson':

              if self.exit_gate == 'track_j_gate':
                  self.route_from = self.route_from_matson_track_J
                  self.env.update_section_count_cars('6')
                  self.env.update_section_count_cars('5')

              elif self.exit_gate == 'Bluff_gate':
                  self.route_from = self.route_from_matson_Bluff
                  self.env.update_section_count_cars('7')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('5')

              else:
                  self.route_from = self.route_from_matson_main
                  self.env.update_section_count_cars('1')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('5')

            if self.destination == 'Tote':

              if self.exit_gate == 'track_j_gate':
                  self.route_from = self.route_from_tote_track_J
                  self.env.update_section_count_cars('6')
                  self.env.update_section_count_cars('4')

              elif self.exit_gate == 'Bluff_gate':
                  self.route_from = self.route_from_tote_Bluff
                  self.env.update_section_count_cars('7')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('4')
              else:
                  self.route_from = self.route_from_matson_main
                  self.env.update_section_count_cars('1')
                  self.env.update_section_count_cars('3')
                  self.env.update_section_count_cars('4')

        if self.is_arrival_today(self.arrival_seconds):
            # Check the first segment and use the appropriate gate
            if self.entrance_gate == 'track_j_gate':
                self.queue_length = len(self.track_j_gate.queue)
                with self.track_j_gate.request() as track_j_request:
                    yield track_j_request
                    at_the_gate = self.env.simpy_environment.now
                    yield self.env.simpy_environment.timeout(np.round(random.randint(10, 20)))
                    self.enter_the_port = self.env.simpy_environment.now

            elif self.entrance_gate == 'Bluff_gate':
                self.queue_length = len(self.Bluff_gate.queue)
                with self.Bluff_gate.request() as Bluff_gate_request:
                    yield Bluff_gate_request
                    at_the_gate = self.env.simpy_environment.now
                    yield self.env.simpy_environment.timeout(np.round(random.randint(10, 20)))
                    self.enter_the_port = self.env.simpy_environment.now

            else:
                self.queue_length = len(self.check_in.queue)
                with self.check_in.request() as check_in_request:
                    yield check_in_request
                    at_the_gate = self.env.simpy_environment.now
                    yield self.env.simpy_environment.timeout(np.round(random.randint(10, 20)))
                    self.enter_the_port = self.env.simpy_environment.now


            # Compute Travel Time
            self.gate_to_station_time = self.transportation_time(self.route_to)
            yield self.env.simpy_environment.timeout(self.gate_to_station_time)

            # Logic for processing at the destination for Trucks
            if self.vehicle_type == 'Truck' and self.is_arrival_today(self.arrival_seconds):
                self.enter_containeryard_time = self.env.simpy_environment.now

                time_ranges = [(600, 750), (500, 600), (900, 1200)]
                probabilities = [0.5, 0.3, 0.2]

                selected_range = random.choices(time_ranges, probabilities, k=1)[0]

                self.unloading_loading = random.randint(selected_range[0], selected_range[1])

                yield self.env.simpy_environment.timeout(self.unloading_loading)
                self.finish_unloading_loading = self.env.simpy_environment.now

                # Process in hazmat lane if required
                if random.random() < 0.125:
                    with self.hazmat_lane.request() as hazmat_request:
                        self.hazmat_arrive = self.env.simpy_environment.now
                        yield hazmat_request
                        self.hazmat_enter = self.env.simpy_environment.now
                        self.hazmat_process = random.randint(5, 15)
                        yield self.env.simpy_environment.timeout(self.hazmat_process)

                # Maintenance if required
                if random.random() < 0.1:
                    self.maintenance_process = random.randint(600, 900)
                    yield self.env.simpy_environment.timeout(self.maintenance_process)

            # Process the route from the destination
            yield self.env.simpy_environment.timeout(self.transportation_time(self.route_from))

            self.waiting_time = self.enter_the_port - self.arrival_time
            self.cycle_time = self.env.simpy_environment.now - self.arrival_time

            if self.vehicle_type == 'Truck' and self.is_arrival_today(self.arrival_seconds):
                self.waiting_times[self.hour].append(self.waiting_time)
                self.cycle_times[self.hour].append(self.cycle_time)
                self.queue_lengths[self.hour].append(self.queue_length)

class Environment:
    def __init__(self, incoming_distribution, outgoing_distribution, today_date):
        self.simpy_environment = simpy.Environment()
        self.today_date = today_date
        self.check_in = simpy.Resource(self.simpy_environment, capacity=1)
        self.track_j_gate = simpy.Resource(self.simpy_environment, capacity=1)
        self.Bluff_gate = simpy.Resource(self.simpy_environment, capacity=1)
        self.hazmat_lane = simpy.Resource(self.simpy_environment, capacity=1)
        self.incoming_distribution = incoming_distribution
        self.outgoing_distribution = outgoing_distribution
        self.cycle_times = {hour: [] for hour in range(24)}
        self.waiting_times = {hour: [] for hour in range(24)}
        self.hourly_counts_cars = {hour: 0 for hour in range(24)}
        self.hourly_counts_trucks = {hour: 0 for hour in range(24)}
        self.daily_counts_cars = {day: 0 for day in range(1, 32)}
        self.daily_counts_trucks = {day: 0 for day in range(1, 32)}
        self.weekly_counts_cars = {day: 0 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        self.weekly_counts_trucks = {day: 0 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        self.section_counts_cars = {str(section): 0 for section in range(1, 8)}
        self.section_counts_trucks = {str(section): 0 for section in range(1, 8)}
        self.queue_lengths = {hour: [] for hour in range(24)}

    def update_daily_count_cars(self, day_of_month):
        """Increment the count for a specific day of the month."""
        self.daily_counts_cars[day_of_month] += 1

    def update_daily_count_trucks(self, day_of_month):
        """Increment the count for a specific day of the month."""
        self.daily_counts_trucks[day_of_month] += 1

    def update_weekly_count_cars(self, day_of_week):
        """Increment the count for a specific day of the week."""
        self.weekly_counts_cars[day_of_week] += 1

    def update_weekly_count_trucks(self, day_of_week):
        """Increment the count for a specific day of the week."""
        self.weekly_counts_trucks[day_of_week] += 1

    def update_hourly_count_cars(self, hour):
        """Increment the count for a specific hour of the day."""
        self.hourly_counts_cars[hour] += 1

    def update_hourly_count_trucks(self, hour):
        """Increment the count for a specific hour of the day."""
        self.hourly_counts_trucks[hour] += 1

    def update_section_count_cars(self, section):
        """Increment the count for a specific section."""
        self.section_counts_cars[section] += 1

    def update_section_count_trucks(self, section):
        """Increment the count for a specific section."""
        self.section_counts_trucks[section] += 1

    def add_vehicle(self, name, arrival_time, vehicle_type, check_in, track_j_gate, Bluff_gate, hazmat_lane, waiting_times,
                    cycle_times, queue_lengths, incoming_distribution, outgoing_distribution, today_date):
        # Create a Vehicle instance and pass `self` as the environment
        vehicle = Vehicle(environment=self, name=name, arrival_time=arrival_time, vehicle_type=vehicle_type, check_in=check_in,
                          track_j_gate=track_j_gate, Bluff_gate=Bluff_gate, hazmat_lane=hazmat_lane, waiting_times=waiting_times,
                          cycle_times=cycle_times, queue_lengths=queue_lengths, incoming_distribution=incoming_distribution,
                          outgoing_distribution=outgoing_distribution, today_date=today_date)

        # Schedule the vehicle run in the simulation
        self.simpy_environment.process(vehicle.run())  # Assuming immediate start, adjust as needed

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to convert numpy types to Python native types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyJSONEncoder, self).default(obj)

class Executor:
    def __init__(self, truck_file, car_file, incoming_distribution, outgoing_distribution, today_date):

        self.incoming_distribution = incoming_distribution
        self.outgoing_distribution = outgoing_distribution
        self.today_date = today_date
        self.truck_file = truck_file
        self.car_file = car_file
        self.schedules = self.scheduler()
        self.truck_arrival_schedule_mean = self.schedules['truck']['mean']
        self.car_arrival_schedule_mean = self.schedules['car']['mean']
        self.truck_arrival_schedule_mean_minus_std = self.schedules['truck']['mean_minus_std']
        self.car_arrival_schedule_mean_minus_std = self.schedules['car']['mean_minus_std']
        self.truck_arrival_schedule_mean_plus_std = self.schedules['truck']['mean_plus_std']
        self.car_arrival_schedule_mean_plus_std = self.schedules['car']['mean_plus_std']
        self.env1 = self.run_simulation(self.truck_arrival_schedule_mean, self.car_arrival_schedule_mean, self.incoming_distribution, self.outgoing_distribution, self.today_date)
        self.env2 = self.run_simulation(self.truck_arrival_schedule_mean_minus_std, self.car_arrival_schedule_mean_minus_std, self.incoming_distribution, self.outgoing_distribution, self.today_date)
        self.env3 = self.run_simulation(self.truck_arrival_schedule_mean_plus_std, self.car_arrival_schedule_mean_plus_std, self.incoming_distribution, self.outgoing_distribution, self.today_date)

        self.plot_weekly_counts_cars()
        self.plot_hourly_counts_cars()
        self.plot_weekly_counts_trucks()
        self.plot_hourly_counts_trucks()
        self.plot_cycle_times()
        self.plot_waiting_times()
        self.plot_max_queue_length()
        self.save_stats_and_plot_section_counts_cars()
        self.save_stats_and_plot_section_counts_trucks()
        self.save_correlation_data_as_json_month()
        self.save_correlation_data_as_json_week()


    def get_formatted_date(self):
      return self.today_date.strftime('%Y-%m-%d')

    def run_simulation(self,truck_arrival_schedule, car_arrival_schedule, incoming_distribution, outgoing_distribution, today_date):
        env = Environment(incoming_distribution, outgoing_distribution,today_date)

        truck_arrival_schedule = [(time, "Truck") for time in truck_arrival_schedule]
        car_arrival_schedule = [(time, "Car") for time in car_arrival_schedule]

        for arrival_time, vehicle_type in sorted(truck_arrival_schedule + car_arrival_schedule, key=lambda x: x[0]):
            vehicle_name = f"{vehicle_type}_{arrival_time}"
            env.add_vehicle(name=vehicle_name, arrival_time=arrival_time, vehicle_type=vehicle_type, check_in=env.check_in,
                            track_j_gate=env.track_j_gate, Bluff_gate=env.Bluff_gate,
                            hazmat_lane=env.hazmat_lane,
                            waiting_times=env.waiting_times, cycle_times=env.cycle_times,
                            queue_lengths=env.queue_lengths,
                            incoming_distribution=incoming_distribution,
                            outgoing_distribution=outgoing_distribution, today_date=env.today_date)

        last_arrival_time = max(truck_arrival_schedule + car_arrival_schedule)[0] if truck_arrival_schedule + car_arrival_schedule else 0
        env.simpy_environment.run(until=last_arrival_time)

        return env

    def scheduler(self):
        truck_processor = TrafficDataProcessor(self.truck_file, self.today_date)
        car_processor = TrafficDataProcessor(self.car_file, self.today_date)

        schedules = {
            'truck': {
                'mean': truck_processor.create_arrival_schedule_for_current_month(mode='mean'),
                'mean_minus_std': truck_processor.create_arrival_schedule_for_current_month(mode='mean-minus-std'),
                'mean_plus_std': truck_processor.create_arrival_schedule_for_current_month(mode='mean-plus-std'),
            },
            'car': {
                'mean': car_processor.create_arrival_schedule_for_current_month(mode='mean'),
                'mean_minus_std': car_processor.create_arrival_schedule_for_current_month(mode='mean-minus-std'),
                'mean_plus_std': car_processor.create_arrival_schedule_for_current_month(mode='mean-plus-std'),
            }
        }

        # Return the created schedules
        return schedules

    def count_specific_weekday_in_current_month(self, weekday_name):
        """Counts occurrences of a specific weekday in the current month."""
        start_of_month = self.today_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = start_of_month.replace(month=start_of_month.month % 12 + 1) if start_of_month.month < 12 else start_of_month.replace(year=start_of_month.year + 1, month=1)
        end_of_month = next_month - timedelta(days=1)

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_number = weekdays.index(weekday_name)

        count = 0
        current_day = start_of_month
        while current_day <= end_of_month:
            if current_day.weekday() == weekday_number:
                count += 1
            current_day += timedelta(days=1)

        return count

    def save_correlation_data_as_json_week(self):
        file_name = f'correlation_data_weeks_{self.get_formatted_date()}.json'
        processor = TrafficDataProcessor(self.truck_file, self.today_date)
        max_length = 0
        for values in processor.data.values():
            if len(values) > max_length:
                max_length = len(values)
        all_data = {day: [] for day in processor.days}

        for (month, day, hour), values in processor.data.items():
            padded_values = np.array(values + [np.mean(values)] * (max_length - len(values)))
            all_data[day].extend(padded_values)

        df_data = pd.DataFrame(all_data)
        correlation_matrix = df_data.corr()

        correlation_json = correlation_matrix.to_json()
        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        file_name = dashboard_path + file_name
        with open(file_name, 'w') as f:
            f.write(correlation_json)

    def save_correlation_data_as_json_month(self):
        file_name = f'correlation_data_months_{self.get_formatted_date()}.json'
        processor = TrafficDataProcessor(self.truck_file, self.today_date)
        max_length = 0
        for values in processor.data.values():
            if len(values) > max_length:
                max_length = len(values)

        # Creating a dictionary to hold monthly data with month names as keys
        all_data = {
            'Jan': [], 'Feb': [], 'Mar': [], 'Apr': [], 'May': [], 'Jun': [],
            'Jul': [], 'Aug': [], 'Sep': [], 'Oct': [], 'Nov': [], 'Dec': []
        }

        for (month, day, hour), values in processor.data.items():
            month_key = month  # Assume month is already a string like 'Jan', 'Feb', etc.
            padded_values = values + [np.mean(values)] * (max_length - len(values))
            all_data[month_key].extend(padded_values)

        df_data = pd.DataFrame(all_data)
        correlation_matrix = df_data.corr()

        correlation_json = correlation_matrix.to_json()

        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        file_name = dashboard_path + file_name

        with open(file_name, 'w') as f:
            f.write(correlation_json)


    def plot_weekly_counts_trucks(self):
        processor = TrafficDataProcessor(self.truck_file, self.today_date)
        processor.calculate_weekly_arrival_stats()
        processor.plot_weekly_arrival_stats_and_save_trucks()

    def plot_weekly_counts_cars(self):
        processor = TrafficDataProcessor(self.car_file, self.today_date)
        processor.calculate_weekly_arrival_stats()
        processor.plot_weekly_arrival_stats_and_save_cars()

    def plot_hourly_counts_trucks(self):
        hourly_counts_1 = self.env1.hourly_counts_trucks
        hourly_counts_2 = self.env2.hourly_counts_trucks
        hourly_counts_3 = self.env3.hourly_counts_trucks

        hourly_sorted = sorted(hourly_counts_1.keys())
        counts_sorted_1 = [np.round(hourly_counts_1[hour]) for hour in hourly_sorted]
        counts_sorted_2 = [np.round(hourly_counts_2[hour]) for hour in hourly_sorted]
        counts_sorted_3 = [np.round(hourly_counts_3[hour]) for hour in hourly_sorted]

        data_for_json = {
            'hourly_sorted': hourly_sorted,
            'Mean': counts_sorted_1,
            'Lower Bound': counts_sorted_2,
            'Upper Bound': counts_sorted_3,
        }

        json_filename = f'hourly_counts_trucks_{self.get_formatted_date()}.json'

        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_filename = dashboard_path + json_filename
        with open(json_filename, 'w') as json_file:
            json.dump(data_for_json, json_file, indent=4, cls=NumpyJSONEncoder)

        return json_filename

    def plot_hourly_counts_cars(self):
        hourly_counts_1 = self.env1.hourly_counts_cars
        hourly_counts_2 = self.env2.hourly_counts_cars
        hourly_counts_3 = self.env3.hourly_counts_cars

        hourly_sorted = sorted(hourly_counts_1.keys())
        counts_sorted_1 = [np.round(hourly_counts_1[hour]) for hour in hourly_sorted]
        counts_sorted_2 = [np.round(hourly_counts_2[hour]) for hour in hourly_sorted]
        counts_sorted_3 = [np.round(hourly_counts_3[hour]) for hour in hourly_sorted]

        data_for_json = {
            'hourly_sorted': hourly_sorted,
            'Mean': counts_sorted_1,
            'Lower Bound': counts_sorted_2,
            'Upper Bound': counts_sorted_3,
        }

        json_filename = f'hourly_counts_cars_{self.get_formatted_date()}.json'
        
        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_filename = dashboard_path + json_filename
        with open(json_filename, 'w') as json_file:
            json.dump(data_for_json, json_file, indent=4, cls=NumpyJSONEncoder)

        return json_filename

    def plot_cycle_times(self):
        cycle_times = self.env1.cycle_times
        average_cycle_times = {hour: np.mean(times) if times else None for hour, times in cycle_times.items()}
        max_cycle_times = {hour: max(times) if times else None for hour, times in cycle_times.items()}

        hours = list(average_cycle_times.keys())
        average_times = list(average_cycle_times.values())
        max_times = [max_cycle_times[hour] for hour in hours]

        data_for_json = {
            'hours': hours,
            'average_cycle_times': [None if x is None or np.isnan(x) else x for x in average_times],
            'max_cycle_times': [None if x is None or np.isnan(x) else x for x in max_times]
        }

        json_filename = f'cycle_times_{self.get_formatted_date()}.json'
        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_filename = dashboard_path + json_filename
        with open(json_filename, 'w') as json_file:
            json.dump(data_for_json, json_file, indent=4, cls=NumpyJSONEncoder)

        return json_filename

    def plot_waiting_times(self):
        waiting_times = self.env1.waiting_times
        average_waiting_times = {hour: np.mean(times) if times else None for hour, times in waiting_times.items()}
        max_waiting_times = {hour: max(times) if times else None for hour, times in waiting_times.items()}

        hours = list(average_waiting_times.keys())
        average_times = list(average_waiting_times.values())
        max_times = [max_waiting_times[hour] for hour in hours]

        data_for_json = {
            'hours': hours,
            'average_cycle_times': [None if x is None or np.isnan(x) else x for x in average_times],
            'max_cycle_times': [None if x is None or np.isnan(x) else x for x in max_times]
        }

        json_filename = f'waiting_times_{self.get_formatted_date()}.json'

        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_filename = dashboard_path + json_filename

        with open(json_filename, 'w') as json_file:
            json.dump(data_for_json, json_file, indent=4, cls=NumpyJSONEncoder)

        return json_filename


    def plot_max_queue_length(self):
        plt.figure(figsize=(15, 6))

        max_queue_lengths_1 = {hour: max(lengths) if lengths else 0 for hour, lengths in self.env1.queue_lengths.items()}
        max_queue_lengths_2 = {hour: max(lengths) if lengths else 0 for hour, lengths in self.env2.queue_lengths.items()}
        max_queue_lengths_3 = {hour: max(lengths) if lengths else 0 for hour, lengths in self.env3.queue_lengths.items()}

        # Preparing data for JSON
        data_for_json = {
            'most_likely': max_queue_lengths_1,
            'optimistic': max_queue_lengths_2,
            'pessimistic': max_queue_lengths_3,
        }

        json_filename = f'max_queue_lengths_data_{self.get_formatted_date()}.json'
       
        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_filename = dashboard_path + json_filename

        with open(json_filename, 'w') as json_file:
            json.dump(data_for_json, json_file, indent=4, cls=NumpyJSONEncoder)

        return json_filename

    def save_stats_and_plot_section_counts_trucks(self):
        # Collect data from different environments
        mean_counts = self.env1.section_counts_trucks

        # Define section names
        section_names = {
            '1': 'Entry/Exit Checkpoint',
            '2': 'Marathon Rd',
            '3': 'Roger Graves Rd',
            '4': 'Terminal Rd',
            '5': 'Anchorage Port Rd',
            '6': 'Track J Access Rd',
            '7': 'Bluff Rd'
        }

        # Create a DataFrame from the collected data
        sections = list(mean_counts.keys())
        df_stats = pd.DataFrame({
            'Section ID': sections,
            'Section Name': [section_names[section] for section in sections],
            'Mean Count': [mean_counts[section] for section in sections]
        })

        # Sort the DataFrame by Section ID for consistency
        df_stats.sort_values(by='Section ID', inplace=True)

        # Save statistics to a JSON file, including section names
        json_file_path = f'section_counts_trucks_{self.get_formatted_date()}.json'

        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_file_path = dashboard_path + json_file_path

        df_stats.to_json(json_file_path, orient='records', lines=False)

        return json_file_path

    def save_stats_and_plot_section_counts_cars(self):
        # Collect data from different environments
        mean_counts = self.env1.section_counts_cars

        # Define section names
        section_names = {
            '1': 'Entry/Exit Checkpoint',
            '2': 'Marathon Rd',
            '3': 'Roger Graves Rd',
            '4': 'Terminal Rd',
            '5': 'Anchorage Port Rd',
            '6': 'Track J Access Rd',
            '7': 'Bluff Rd'
        }

        # Create a DataFrame from the collected data
        sections = list(mean_counts.keys())
        df_stats = pd.DataFrame({
            'Section ID': sections,
            'Section Name': [section_names[section] for section in sections],
            'Mean Count': [mean_counts[section] for section in sections]
        })

        # Sort the DataFrame by Section ID for consistency
        df_stats.sort_values(by='Section ID', inplace=True)

        # Save statistics to a JSON file, including section names
        json_file_path = f'section_counts_cars_{self.get_formatted_date()}.json'
        root_path = os.environ.get("BASE_PATH")
        dashboard_path = root_path + "/dashboard/tmp/"
        json_file_path = dashboard_path + json_file_path
        df_stats.to_json(json_file_path, orient='records', lines=False)

        return json_file_path

