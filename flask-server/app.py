from flask import Flask, request, send_file, abort, send_from_directory, Response, jsonify, current_app
from flask_cors import CORS  # Import CORS
from flask_bcrypt import Bcrypt
import json
from config import ApplicationConfig
from services.user_service import UserService
from config import ApplicationConfig
import os
import uuid
import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler
from services.subscribe_service import SubscribeService
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mimetypes
from scenarioanalysis import AKDOT_ObjectOriented_Shortterm as shortTerm
from scenarioanalysis import AKDOT_ObjectOriented_Longterm as longTerm
from datetime import datetime
from services.incident_service import IncidentService 
from services.dashboard_service import DashboardService
from services.scenario_analysis import ScenarioAnalysisService
from risk.riskanalysis import RiskAnalysis
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
# Session(app)

app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)
cors = CORS(app, supports_credentials=True)  # Configure CORS first


'''
    session dictionary
'''
sessions = {}

scheduler = BackgroundScheduler()

def generate_dashboard_jsons():
    dashboard_service = DashboardService()
    try:
        dash_board_response = dashboard_service.generate_dashboard_jsons()
        
    except Exception as e:
        print("Exception occured during Json Generation ",e)
        


# Add a job that runs every 10 seconds
scheduler.add_job(func=generate_dashboard_jsons, trigger="cron", hour=0, minute=30)

# Start the scheduler
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

def run_simulations():
    pass
scheduler = BackgroundScheduler()
scheduler.add_job(run_simulations, 'interval', days= 1)
scheduler.start()

'''
    Check if the session token sent by client is valid and return the username for the session token
'''
def is_authenticated(session_token):
    print(session_token)
    print(sessions)
    if session_token in sessions:
        print("Logged in as - " + sessions[session_token])
        return sessions[session_token]
    raise Exception("Unauthorized request")


@app.route('/is_authenticated', methods=['GET'])
def is_user_authenticated():
    session_token = request.headers.get('session-token')
    if session_token in sessions:
        return json.dumps({'response': True}), 200
    else:
        return json.dumps({'response': False}), 401

@app.route('/userdetails', methods=['GET'])
def getUserDetails():
    username = request.args.get('username')
    if(None == username):
        return json.dumps({'response': "Invalid Username"}), 500
    
    try:
        user_service = UserService()
        user_details = user_service.get_user(username)
        return json.dumps({'response': user_details})
    except Exception as e:
        return json.dumps({'response': str(e)}), 500

@app.route('/register', methods=['POST'])
def register_user():
    user_details = request.json
    username = user_details.get('username')
    user_service = UserService()
    if(not username):
        return json.dumps({'response': "User Name is Null"}), 401
    elif(user_service.check_user(username)):
        return json.dumps({'response': "User Name already exists"}), 401
    else:
        response = user_service.create_user(user_details)
        if(response.get('status')== "success"):
            return json.dumps({'response': "User created successfully"}), 201
        else:
            return json.dumps({'response': "Failed to create user"}), 500
        

@app.route('/login', methods=['POST'])
def do_login():
    # Your login logic here
    login_details = request.get_json(force=True)
    username = login_details['username']
    password = login_details['password']
    user_service = UserService()
    if(user_service.check_user(username) and user_service.check_password(username, password)):

        print("Creating session for user " + username)
        session_token = str(uuid.uuid4())
        sessions[session_token] = str(username)
        

        return json.dumps({'response': {"session_token" : session_token, "username": username}}), 200
    else:
        return json.dumps({'response': "Incorrect Credentials"}), 401
    
@app.route('/videoUrls', methods = ['POST'])
def getVideoUrls():
    data = request.json
    block = data.get('disruption_location')
    in_out_route = data.get('inOutRoute')
    analysis_type = data.get('analysis_type')
    video_url_before = ""
    video_url_after = ""
    print(current_app.root_path)
    if(analysis_type == "shortTerm"):
        video_url_before, video_url_after = shortTerm.get_video_links(block, in_out_route)
    elif(analysis_type == "longTerm"):
        video_url_before, video_url_after = longTerm.get_video_links(block, block)
    return jsonify({
        'video_url_before' : video_url_before,
        'video_url_after' : video_url_after
    })

@app.route('/scenario_analysis/plots_suggestions', methods=['GET'])
def get_plots():
    
    if(None == request.args.get('type')):
        return jsonify({'response': "Please provide the type of analysis"}), 400
    analysis_type = request.args.get('type')
    

    path = os.environ.get("BASE_PATH")
    data_path = path + '/scenarioanalysis/data/'

    if(analysis_type == 'short'):

        fileNames = ['cycle_data', 'waiting_data','simulation_results']
    else:
        fileNames = ['average_cycle_times', 'average_waiting_times', 'hazmat_wait_times', 'simulation_results']

    plots_data = {}

    for file in fileNames :

        try:
            file_path = data_path + file + '_' + analysis_type + '.json'
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                plots_data[file] = data
        except FileNotFoundError:
        # Handle the case where the file is not found
            return jsonify({'error': 'File not found -' + file_path}), 404
    


    return jsonify(plots_data), 200


@app.route('/scenario_analysis', methods=['POST'])
def process_request():
    data = request.json
    scenario_analysis = ScenarioAnalysisService()
    
    # check of the date can be passed in the normal format and 
    #we convert the date to the required the data in the backend
    
    analysis_type = data.get('analysis_type')
    suggestions = ""
    if analysis_type == 'shortTerm':
        # Defining the path for Excel files
        # can use the current_app.root_path to get the flask directory and use the  
        # relative path to the Excel file

        disruption_length = data.get('disruption_length')
        disruption_location = data.get('disruption_location')
        in_out_route = data.get('inOutRoute')
        date = datetime.strptime(data.get("date_hour"), "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d %b %Y")

        hour = data.get('hour')
        # Below function should be called inorder to run scenario analysis
        suggestions = scenario_analysis.runShortTerm(disruption_location, in_out_route, disruption_length, date, hour)

    elif analysis_type == "longTerm":
        # remove after implementing longterm
        absolute_path_of_file = os.environ.get('BASE_PATH')
        scenario_path = "/scenarioanalysis/"
        
        file_directory = absolute_path_of_file + scenario_path
        excel_file_trucks = os.path.join(file_directory, "AKDOTTrucks.xlsx")
        excel_file_cars = os.path.join(file_directory, "AKDOTCars.xlsx")
        # get params from front end once the integration completes
        """
            car_excel : from files
            truck_excel : from files
            start_date : from input fe format -> '21 Dec 2023'
            end_date : from input fe fromat -> '27 Dec 2023'
            block location : from input fe 
            route distribution : from fe [0,1] or [1,0] for now. format {block : [1,0]}
            month start dat derive from start date.
        """
        # Validate params
        # change input format to this format and as string
        if(None != data.get("start_date") and None != data.get("end_date")):

            start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").strftime("%d %b %Y")
            end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").strftime("%d %b %Y")

        block = data.get("block_location")
        disruption_length = data.get("route_distribution")
        route_distribution = {block: disruption_length}
        # this will generate the plots as well if needed we can seperate the plots from the below method and genersate the graphs seperately
        env = scenario_analysis.runLongTerm(start_date=start_date, end_date=end_date,block=block,route_distribution=route_distribution)
        
        
    return jsonify({
        'success': True
    })


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Define the directory where your files are stored
    staging_dir_url = os.environ.get('BASE_PATH')
    file_directory = staging_dir_url + "/scenarioanalysis/data/"

    # Construct the full file path
    file_path = os.path.join(file_directory, filename+".png")

    # Check if file exists
    if not os.path.isfile(file_path):
        # If the file does not exist, return a 404 error
        abort(404)

    # If the file exists, send it as a response
    return send_file(file_path, as_attachment=True)


@app.route('/files/<filename>')
def get_file(filename):
    staging_dir_url = os.environ.get('BASE_PATH')
    file_directory = staging_dir_url + "/scenarioanalysis/data/"
    file_path = os.path.join(file_directory, filename)
    mime_type, _ = mimetypes.guess_type(file_path)

    if(filename == "video.mp4"):
        print(file_path)
        print(mime_type)
    if mime_type == 'video/mp4':
        print("video")
        return Response(open(file_path, 'rb'), content_type=mime_type)
    else:
        return send_from_directory(file_directory, filename)
    
@app.route('/dashboardfiles/<filename>')
def get_dashboard_file(filename):
    staging_dir_url = os.environ.get('BASE_PATH')
    file_directory = staging_dir_url + "/dashboard/data/"
    file_path = os.path.join(file_directory, filename)
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type == 'video/mp4':
        print("video")
        return Response(open(file_path, 'rb'), content_type=mime_type)
    else:
        return send_from_directory(file_directory, filename)
    

'''
    Rest end points to logout the authenticated user
'''
@app.route('/logout', methods=['POST'])
def do_logout():
    global sessions
    session_token = request.headers.get('session-token')
    print("Deleting session for user " +  sessions[session_token])   
    del sessions[session_token]
    return json.dumps({'response': 'success'}), 200


@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        subscribe_data = request.json

        sub_service = SubscribeService()

        inserted_id = sub_service.put_subscribe_data(subscribe_data)
        # Example usage
        if subscribe_data['communication'] == 'Email': 
            sub_service.send_email(
                subject="Port of Alaska Alerts Service: Subscription Confirmation",
                message="Congratulation 🎉 You have subscribed for email notifications from AKDOT",
                to_addr=subscribe_data['email'],
                name = subscribe_data['fullName'],
                from_addr="yhemanthsai555@gmail.com",
                password="rcxv qeec psfy sadk"
            )

        elif subscribe_data['communication'] == 'Text': 
            sub_service.send_textmessage(
                #Check if key for the dict is text or some other
                to = subscribe_data['mobile'],
                message =  "Congratulations🎉 You have subscribed for text notifications from Port of Alaska. You will now receive important notifications and updates regarding port operations, weather advisories, and other pertinent information directly to mobile."
            )

        return jsonify({"message": "Data stored successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""
    This Api adds an incident.
    sample request json
    {
    "dateTime": String,
    "description": String,
    "exactLocation": String,
    "geolocation": {
        "latitude": float,
        "longitude": float
    },
    "priorityLevel": String,
    "recipients": String of emails with semi-colon separated,
    "incidentName": String,
    "incidentType": String,
    "suggestions": String
    }


"""
@app.route("/addincident", methods=["POST"])
def add_incident():
    #validate

    incident_data = request.json
    if(not incident_data):
        return jsonify({"msg":"Missing JSON in request!"}) ,400
    if(None == incident_data.get('incidentName') or "" == incident_data.get('incidentName')):
        return jsonify({"msg":"Missing Incident Name in request!"}) ,400
    if(None == incident_data.get('dateTime') or "" == incident_data.get('dateTime')):
        return jsonify({"msg":"Missing Incident Time in request!"}) ,400
    #pass values to service
    try :
        incidentService =  IncidentService()
        res = incidentService.create_incident(incident_data)
        return jsonify({"success":True}) ,201
    except ValueError as ve:
        return jsonify({"error":str(ve)}) , 400
    except Exception as e:
        return jsonify({"error":str(e)}),500



@app.route("/getincidents", methods=["GET"])
def get_all_incidents():

    # check for params


    try: 
        incidentService =  IncidentService()
        # call the service to get all the data
        incident_records = incidentService.get_all_open_incidents()

        #check if pagination is required or not

        # send the incidents
        print(incident_records)
        return jsonify(incident_records), 200
    except Exception as e:
        return jsonify({"error":str(e)}), 500

    
"""
    This Api updates an incident.
    sample request json
    {
    "dateTime": String,
    "description": String,
    "exactLocation": String,
    "geolocation": {
        "latitude": float,
        "longitude": float
    },
    "priorityLevel": String,
    "affliation":[list of afflitiations]
    "otherRecipients": String of emails with semi-colon separated,
    "incidentName": String,
    "incidentType": String,
    "suggestions": String
    }


"""
@app.route("/incident/<incidentId>", methods=["PUT"])
def update_incident(incidentId):
    
    # check if incident exits ot not
    # validate the incoming data
    #  validate the request body
    try:
        incidentService =  IncidentService()
        if(None == incidentId):
            return jsonify({"msg":"Missing incident parameter in request!"}) ,400
        incident_data = request.json
        response =  incidentService.update_incident(incidentId,incident_data)
        if(None == response):
            return jsonify({"msg":"Incident does not exist"}),404
        
        if(response):
            return jsonify({"updated":True}),200
        return jsonify({"updated":False}),200

    except Exception as e:
        return jsonify({"error":"Error occured while processing your request" + str(e)}), 400

    # call service method  with new details

    # send response
    return json.dumps({'response': 'success'}), 200

@app.route("/closeincident/<incidentId>", methods=["PUT"])
def delete_incident(incidentId):

    # check if incident exists or not
    try:
        incidentService =  IncidentService()
        if(None == incidentId):
            return jsonify({"msg":"Missing incident parameter in request!"}) ,400
        
        # call service to delete the incodent
        response = incidentService.close_incident(incidentId)
        if(None == response):
             return jsonify({"msg":"Incident does not exist"}),404
        elif(False==response):
             return jsonify({"msg":"Error while deleting the incident"}) ,500
        else :
            return  jsonify({"success":True}),200

    except Exception  as e :
        return jsonify({"error":"Error occured while processing your request" + str(e)}),400
    


    

@app.route("/incident/<incidentId>", methods=["GET"])
def get_incident(incidentId):
    # check if incident exists or not
    # if exists call the service to fetch the details and send the data
    try :
        incidentService =  IncidentService()
        if(None == incidentId):
            return jsonify({"msg":"Missing incident parameter in request!"}) ,400
        incident = incidentService.get_incident(incidentId)
        if None == incident:
             return jsonify({"msg":"Incident does not exist"}),404
        return jsonify(incident), 200
    except Exception as e:
        print("Exception Occured while getting incident ",e)
        return jsonify({"error": "Error occured while processing your request"}),500 

@app.route("/dashboard/<graphID>", methods=["GET", "POST"])
def getDashBoardGraphs(graphID):
    # validate the graph parameters and differentiate between graphs car, truck, both

    # after successfull validation, call the serivice that connect to simpy models to get graph data

    # convert to required json as per graphs

    # return values 
    pass

@app.route("/getfrequency/<frequency_type>", methods=["GET"])
def get_frequency_per_type(frequency_type):
    """
        Returns the frequency of incidents based on the passed incident type
    """
    if(None == frequency_type):
        return jsonify({"msg":"Missing frequency in request!"}) ,400
    try:
        incidentService =  IncidentService()
        frequency_data = incidentService.get_frequency_per_type(frequency_type)
        return jsonify(frequency_data),200
    except Exception as e:
        print("Exception Occured while getting frequency , e")
        return jsonify({"error": "Error occured while processing your request"}),500 
    
@app.route("/getresloutiontime/<incident_type>", methods=[ "GET"] )
def get_resolution_time(incident_type):
    """
        Return Resloution times per severiarity for a given incidenttype
    """
    if(None ==  incident_type):
        return jsonify({"msg":"Missing incident type in request!"}),400
    try:
        incidentService =  IncidentService()
        reslotuion_time_data = incidentService.get_resolution_time_by_incident_type(incident_type)
        return jsonify(reslotuion_time_data),200   
    except Exception as e:
        print("Exception occured during  retrieving resolution time ",e)
        return jsonify({"error": "Error occured while processing your request"}),500

@app.route("/dashboard/generate_jsons", methods=['POST'])
def  generate_dashboard_json():
    """
        Create required jsons to generate graps for dashboard
    """
    dashboard_service = DashboardService()
    try:
        dash_board_response = dashboard_service.generate_dashboard_jsons()
        return jsonify(dash_board_response),201
    except Exception as e:
        print("Exception occured during Json Generation ",e)
        return jsonify({"status": "failed","error": "Error occured while processing your request"}),500

@app.route("/dashboard/cycle_times",methods=["GET"])
def  dashboard_cycle_times():
    """
        return cycle times json
    """
    days = 0
    if (None != request.args.get('day')):
        days = int(request.args.get('day'))
    today = dt.date.today()
    four_days_from_now = today + dt.timedelta(days=days)
    formatted_date = four_days_from_now.strftime("%Y-%m-%d")
    path = os.environ.get("BASE_PATH")
    dashboard_path = path +  "/dashboard/data/"
    file_name =f"cycle_times_{formatted_date}.json"
    full_file_name = dashboard_path+file_name
    try:
        with open(full_file_name, 'r') as json_file:
        # Load the JSON data into a Python dictionary
            data = json.load(json_file)

        # Return the data as JSON using jsonify
        return jsonify(data), 200

    except FileNotFoundError:
        # Handle the case where the file is not found
        return jsonify({'error': 'File not found'}), 404

    except json.JSONDecodeError:
        # Handle the case where the file content is not valid JSON
        return jsonify({'error': 'Invalid JSON data'}), 400
        

@app.route("/dashboard/hourly_counts",methods=["GET"])
def  dashboard_hourly_counts():
    """
        return Hourly Counts json
    """

    days = 0
    if (None != request.args.get('day')):
        days = int(request.args.get('day'))
    today = dt.date.today()
    four_days_from_now = today + dt.timedelta(days=days)
    formatted_date = four_days_from_now.strftime("%Y-%m-%d")
    vehicle = request.args.get('vehicle')
    path = os.environ.get("BASE_PATH")
    dashboard_path = path +  "/dashboard/data/"
    file_name ="hourly_counts_cars.json"
    if(None != vehicle):
        file_name =f"hourly_counts_{vehicle}_{formatted_date}.json"
    full_file_name = dashboard_path+file_name
    try:
        with open(full_file_name, 'r') as json_file:
        # Load the JSON data into a Python dictionary
            data = json.load(json_file)

        # Return the data as JSON using jsonify
        return jsonify(data), 200

    except FileNotFoundError:
        # Handle the case where the file is not found
        return jsonify({'error': 'File not found'}), 404

    except json.JSONDecodeError:
        # Handle the case where the file content is not valid JSON
        return jsonify({'error': 'Invalid JSON data'}), 400

@app.route("/dashboard/max_queue_length",methods=["GET"])
def  dashboard_max_queue_length():
    """
        return max_queue_length json
    """
    days = 0
    if (None != request.args.get('day')):
        days = int(request.args.get('day'))
    today = dt.date.today()
    four_days_from_now = today + dt.timedelta(days=days)
    formatted_date = four_days_from_now.strftime("%Y-%m-%d")
    path = os.environ.get("BASE_PATH")
    dashboard_path = path +  "/dashboard/data/"
    file_name =f"max_queue_lengths_data_{formatted_date}.json"
    full_file_name = dashboard_path+file_name
    try:
        with open(full_file_name, 'r') as json_file:
        # Load the JSON data into a Python dictionary
            data = json.load(json_file)

        # Return the data as JSON using jsonify
        return jsonify(data), 200

    except FileNotFoundError:
        # Handle the case where the file is not found
        return jsonify({'error': 'File not found'}), 404

    except json.JSONDecodeError:
        # Handle the case where the file content is not valid JSON
        return jsonify({'error': 'Invalid JSON data'}), 400


@app.route("/dashboard/section_counts_stats",methods=["GET"])
def  dashboard_section_count_stats():
    """
        return section_counts_stats json
    """
    days = 0
    if (None != request.args.get('day')):
        days = int(request.args.get('day'))
    today = dt.date.today()
    four_days_from_now = today + dt.timedelta(days=days)
    formatted_date = four_days_from_now.strftime("%Y-%m-%d")
    vehicle = request.args.get('vehicle')
    path = os.environ.get("BASE_PATH")
    dashboard_path = path +  "/dashboard/data/"
    file_name ="section_counts_cars.json"
    if(None != vehicle):
        file_name =f"section_counts_{vehicle}_{formatted_date}.json"

    full_file_name = dashboard_path+file_name
    try:
        with open(full_file_name, 'r') as json_file:
        # Load the JSON data into a Python dictionary
            data = json.load(json_file)

        # Return the data as JSON using jsonify
        return jsonify(data), 200

    except FileNotFoundError:
        # Handle the case where the file is not found
        return jsonify({'error': 'File not found'}), 404

    except json.JSONDecodeError:
        # Handle the case where the file content is not valid JSON
        return jsonify({'error': 'Invalid JSON data'}), 400

@app.route("/dashboard/correlation",methods=["GET"])
def  dashboard_correlations():
    """
        return section_counts_stats json
    """
    days = 0
    if (None != request.args.get('day')):
        days = int(request.args.get('day'))
    today = dt.date.today()
    four_days_from_now = today + dt.timedelta(days=days)
    formatted_date = four_days_from_now.strftime("%Y-%m-%d")
    type = request.args.get('type')
    path = os.environ.get("BASE_PATH")
    dashboard_path = path +  "/dashboard/data/"

    file_name =f"correlation_data_{type}_{formatted_date}.json"

    full_file_name = dashboard_path+file_name
    try:
        with open(full_file_name, 'r') as json_file:
        # Load the JSON data into a Python dictionary
            data = json.load(json_file)

        # Return the data as JSON using jsonify
        return jsonify(data), 200

    except FileNotFoundError:
        # Handle the case where the file is not found
        return jsonify({'error': 'File not found'}), 404

    except json.JSONDecodeError:
        # Handle the case where the file content is not valid JSON
        return jsonify({'error': 'Invalid JSON data'}), 400



@app.route("/dashboard/waiting_times",methods=["GET"])
def  dashboard_waiting_times():
    """
        return waiting_times json
    """
    days = 0
    if (None != request.args.get('day')):
        days = int(request.args.get('day'))
    today = dt.date.today()
    four_days_from_now = today + dt.timedelta(days=days)
    formatted_date = four_days_from_now.strftime("%Y-%m-%d")

    path = os.environ.get("BASE_PATH")
    dashboard_path = path +  "/dashboard/data/"
    file_name =f"waiting_times_{formatted_date}.json"
    full_file_name = dashboard_path+file_name
    try:
        with open(full_file_name, 'r') as json_file:
        # Load the JSON data into a Python dictionary
            data = json.load(json_file)

        # Return the data as JSON using jsonify
        return jsonify(data), 200

    except FileNotFoundError:
        # Handle the case where the file is not found
        return jsonify({'error': 'File not found'}), 404

    except json.JSONDecodeError:
        # Handle the case where the file content is not valid JSON
        return jsonify({'error': 'Invalid JSON data'}), 400


@app.route("/dashboard/weekly_counts",methods=["GET"])
def  dashboard_weekly_counts():
    """
        return Weekly Counts json
    """
    days = 0
    if (None != request.args.get('day')):
        days = int(request.args.get('day'))
    today = dt.date.today()
    four_days_from_now = today + dt.timedelta(days=days)
    formatted_date = four_days_from_now.strftime("%Y-%m-%d")
    
    vehicle = request.args.get('vehicle')
    path = os.environ.get("BASE_PATH")
    dashboard_path = path +  "/dashboard/data/"

    file_name ="weekly_counts_cars.json"
    if None != vehicle:
        file_name ="weekly_counts_"+ vehicle+".json"
    full_file_name = dashboard_path+file_name
    try:
        with open(full_file_name, 'r') as json_file:
        # Load the JSON data into a Python dictionary
            data = json.load(json_file)

        # Return the data as JSON using jsonify
        return jsonify(data), 200

    except FileNotFoundError:
        # Handle the case where the file is not found
        return jsonify({'error': 'File not found'}), 404

    except json.JSONDecodeError:
        # Handle the case where the file content is not valid JSON
        return jsonify({'error': 'Invalid JSON data'}), 400


@app.route("/incident_alerts",methods=["GET"])
def get_incident_alerts():
    """
        This method will send all the alerts from the open incidents
        It considers only the "Maintainance" and the "Accidents and Blockages"

    """
    try:
        incident_service = IncidentService()

        alert_incidents = incident_service.get_alert_incidents()
        return jsonify(alert_incidents), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/riskSection", methods=["GET"])
def get_risk_section():
    """
    This method will send all the risk graphs based on the selected section
    """

    try:
        if None == request.args.get('section'):
            return jsonify({'error': 'Section is required'}), 400
        section = request.args.get('section')
        risk_analysis = RiskAnalysis()
        sectionRisk = risk_analysis.getSectionRisks(section)
        return jsonify(sectionRisk), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route("/riskRoute", methods=["GET"])
def get_risk_route():
    """
    This method will send all the risk graphs based on the selected routes
    """
    try:
        if None == request.args.get('inroute') or None == request.args.get('outroute'):
            return jsonify({'error': 'In and Out Routes are required'}), 400
        
        inroute = request.args.get('inroute')
        outroute = request.args.get('outroute')
        risk_analysis = RiskAnalysis()
        routeRisk = risk_analysis.getAlternateRouteRisks(inroute, outroute)
        return jsonify(routeRisk), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == "__main__":
    app.run(port=7001)
