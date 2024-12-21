from scenarioanalysis import AKDOT_ObjectOriented_Shortterm as shortTerm
from scenarioanalysis import AKDOT_ObjectOriented_Longterm as longTerm
import os
class ScenarioAnalysisService():
    def __init__(self):
        pass

    def runShortTerm(self, disruption_location, in_out_route, disruption_length, date, hour):
        absolute_path_of_file = os.environ.get('BASE_PATH')
        scenario_path = "/scenarioanalysis/"
        file_directory = absolute_path_of_file + scenario_path
        excel_file_trucks = os.path.join(file_directory, "AKDOTTrucks.xlsx")
        excel_file_cars = os.path.join(file_directory, "AKDOTCars.xlsx")

        suggestions = ""
        
        reaction_time = 900
        env = shortTerm.main_execution(excel_file_trucks, excel_file_cars, disruption_location, in_out_route, disruption_length, date, hour, reaction_time)
        if (None != env):
            suggestions = env.suggestions
    
        return suggestions
    
    def runLongTerm(self, start_date, end_date, block, route_distribution):
        absolute_path_of_file = os.environ.get('BASE_PATH')
        scenario_path = "/scenarioanalysis/"
        file_directory = absolute_path_of_file + scenario_path
        excel_file_trucks = os.path.join(file_directory, "AKDOTTrucks.xlsx")
        excel_file_cars = os.path.join(file_directory, "AKDOTCars.xlsx")

        env = longTerm.execute_simulation_and_plotting(excel_file_cars, excel_file_trucks,start_date, end_date,block,route_distribution)
        return env
    
