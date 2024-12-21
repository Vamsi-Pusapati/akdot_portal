from dashboard import akdot_dashboard
import os
from datetime import datetime, timedelta
import shutil

class DashboardService():
    def __init__(self) -> None:
        pass

    def remove_all_files(self, dest_folder):
        for filename in os.listdir(dest_folder):
            file_path = os.path.join(dest_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory and its contents
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    def move_files(self, src_dir, dst_dir):
        for filename in os.listdir(src_dir):
            src_path = os.path.join(src_dir, filename)
            dest_path = os.path.join(dst_dir, filename)
            try:
                shutil.move(src_path, dest_path)
                print(f'Moved {src_path} to {dest_path}')
            except Exception as e:
                print(f'Failed to move {src_path}. Reason: {e}')


    def generate_dashboard_jsons(self):
        absolute_path_of_file = os.environ.get('BASE_PATH')
        dashboard_path = "/dashboard/"
        
        file_directory = absolute_path_of_file + dashboard_path
        excel_file_trucks = os.path.join(file_directory, "AKDOTTrucks.xlsx")
        excel_file_cars = os.path.join(file_directory, "AKDOTCars.xlsx")
        incoming_distribution = [1, 0, 0]  # Example incoming distribution
        outgoing_distribution = [1, 0, 0]  # Example outgoing distribution
        try:
            for i in range(7):
                today_date = datetime.today() + timedelta(days=i)
                executor = akdot_dashboard.Executor(excel_file_trucks, excel_file_cars, incoming_distribution, outgoing_distribution, today_date)

            self.remove_all_files(file_directory+"data") 
            self.move_files(file_directory+"tmp", file_directory+"data")   
            return {"status": "success"}
        except Exception as e:
            print("Error generating JSONs : ", e)
            raise e
    


    