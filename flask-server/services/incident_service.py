from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import uuid
from dao.incident_dao import IncidentDao 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class IncidentService():
    def  __init__(self):
        pass

    def create_incident(self,incident_details):
        # generate uuid
        # get structure the json to be stored
        # call dao method to create the incident
        incident = self.populate_incident(incident_details)
        incident['uid'] = str(uuid.uuid4())
        incident['status'] = "open"
        incident_dao = IncidentDao()
        response = incident_dao.create_incident(incident)
        if(None !=  response and (None != incident_details.get('otherRecipients')) or 
           (None != incident_details.get('affiliations'))):
            subscribed_mails = []
            other_recipients = []
            if(None != incident_details.get('affiliations')):
                subscribed_mails = incident_dao.get_subscribed_emails(incident_details.get('affiliations'))
            if(None != incident_details.get('otherRecipients')):
                other_recipients = incident_details.get('otherRecipients').split(",")
            emails = list(set(subscribed_mails + other_recipients))
            self.send_notification(emails)
        return response

    def populate_incident(self, incident_details):
        incident = {}
        
        incident['incidentName'] = incident_details.get('incidentName')
        if(None != incident_details.get('dateTime') or '' != incident_details.get('dateTime')):
            incident['dateTime'] = datetime.strptime(incident_details.get('dateTime'), "%Y-%m-%dT%H:%M")

        incident['description'] = incident_details.get('description')
        incident['incidentLocation'] = incident_details.get('exactLocation')
        incident['severityLevel'] = incident_details.get('severityLevel')
        incident['affiliations'] = incident_details.get('affiliations')
        incident['otherRecipients'] = incident_details.get('otherRecipients')
        incident['incidentType'] = incident_details.get('incidentType')
        incident['suggestions'] = incident_details.get('suggestions')
        incident['expectedResolutionTime'] = incident_details.get('expectedResolutionTime')
        if(None != incident_details.get("geolocation")):
            geolocation = {}
            geolocation["latitude"] = incident_details.get("geolocation").get("latitude")
            geolocation["longitude"]= incident_details.get("geolocation").get("longitude")
            incident["geolocation"] = geolocation
        return incident
    
    
    
    def update_incident(self, incident_id, incident_details):
        
        #call the dao to update the incident
        incident_dao = IncidentDao()
        if(None == incident_dao.get_incident(incident_id)):
            return None
        incident = self.populate_incident(incident_details)
        return  incident_dao.update_incident(incident_id,incident)
    

    def get_time_difference_in_sec(self, closedTime, openTime):
        """Calculates the difference between two times in "%Y-%m-%dT%H:%M" format.

        Args:
            time1: The first time string in "%Y-%m-%dT%H:%M" format.
            time2: The second time string in "%Y-%m-%dT%H:%M" format.

        Returns:
            A timedelta object representing the difference between the two times.
        """

        # Parse strings into datetime objects
        closedtime1 = closedTime
        opentime2 = openTime

        # Calculate difference as a timedelta object
        time_difference = closedtime1 - opentime2

        return int(time_difference.total_seconds())        
    
    def close_incident(self, incident_id):
        # call dao to detele an incident from db
        incident_dao = IncidentDao()
        incident_details = incident_dao.get_incident(incident_id)
        if(None == incident_details):
            return None
        incident_details["status"]="closed"
        incident_details["closedDateTime"] = datetime.now()
        incident_details["resolutionTimeInSec"] = self.get_time_difference_in_sec(incident_details.get("closedDateTime"), incident_details.get("dateTime"))
        
        close_response = incident_dao.update_incident(incident_id, incident_details)
        return close_response
    



    def get_incident(self, incident_id):
        # call the dao method to get the open incidents
        incident_dao = IncidentDao()
        incident = incident_dao.get_incident(incident_id)
        if(None == incident):
            return None
        incident_data = {}
        incident_data['uid'] = incident.get('uid')
        incident_data['incidentName'] = incident.get( 'incidentName' )
        incident_data['dateTime'] =  incident.get('dateTime').strftime("%Y-%m-%dT%H:%M")
        incident_data['description'] = incident.get('description')
        incident_data['exactLocation'] = incident.get('incidentLocation')
        incident_data['severityLevel'] = incident.get('severityLevel')
        incident_data['otherRecipients'] = incident.get('otherRecipients')
        incident_data['incidentType'] = incident.get('incidentType')
        incident_data['suggestions'] = incident.get('suggestions')
        incident_data['affiliations'] = incident.get( "affiliations" )
        incident_data['expectedResolutionTime'] = incident.get('expectedResolutionTime')
        if(None !=  incident.get("geolocation")):
            geolocation = incident.get("geolocation")
            incident_data['geolocation'] = geolocation


        return incident_data

    def get_all_open_incidents(self):
        # call the dao method to get all open incidents.
        incident_dao = IncidentDao()
        open_incidents = incident_dao.get_all_open_incidents()
        incidents_data = []
        for  incident in open_incidents:
            data={}
            data['uid'] = incident.get('uid')
            data['incidentName'] = incident.get('incidentName')
            if(None!=incident.get('dateTime')):
                data['dateTime'] = incident.get('dateTime').strftime("%Y-%m-%d %H:%M")
            incidents_data.append(data)
        return incidents_data
    
    def get_alert_incidents(self):
        
        incident_dao = IncidentDao()
        alert_incidents = incident_dao.get_alert_incidents()

        alert_incident_data = []
        for incident in alert_incidents:
            alert_incident_data.append(incident)
        return alert_incident_data
    
    def send_notification(self,emailIds):
        if (None !=  emailIds and len(emailIds)>0):
            for email in emailIds:
                try:   
                    mailId = email.strip()
                    self.send_email(mailId)
                except Exception as e:
                    print(f"Error while sending notification : {e}")
                    continue
    def get_frequency_per_type(self,incidentType):
        incident_dao = IncidentDao()
        incident_records = incident_dao.get_incident_based_on_incidentType(incidentType)
        current_date = datetime.now()
        one_month_ago_datetime = current_date + relativedelta(months=-1)
        one_year_ago_datetime = current_date + relativedelta(years=-1)
        total_count = 0
        monthly_count=0; yearly_count=0
        if(None != incident_records and len(incident_records)>0):
            total_count = len(incident_records)
            for incident in incident_records:
                incident_date_time = incident.get('dateTime')
                if(incident_date_time>=one_month_ago_datetime):
                    monthly_count+=1
                if(incident_date_time>=one_year_ago_datetime):
                    yearly_count+=1
        frequencyData = {
            "last_month": monthly_count,
            "last_year": yearly_count,
            "total": total_count
        }
        return frequencyData
    
    def get_time_format_from_sec(self,no_of_secs):
        time_delta = timedelta(seconds=int(no_of_secs))
        days = time_delta.days
        remaining_seconds = no_of_secs % (24*60*60)
        hours = remaining_seconds // (60 * 60)
        minutes = remaining_seconds  % (60 * 60) // 60
        seconds = remaining_seconds % 60
        timeStr = ""
        if(days > 0):
            timeStr += f"{str(days)} day(s), "
        timeStr += f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)} hrs"
        return timeStr
        
    
    def get_resolution_time_by_incident_type(self, incident_type):
        incident_dao = IncidentDao()
        incident_records = incident_dao.get_incident_based_on_incidentType(incident_type)
        resolution_time= {'low':[],"medium":[],'high':[]}
        if None!=incident_records and len(incident_records)>0:
            for  incident in incident_records:
                if "closed" == incident.get('status') and incident.get('resolutionTimeInSec') >0:
                    if(incident.get('severityLevel') == 'High'):
                        resolution_time['high'].append(incident.get('resolutionTimeInSec'))
                    elif(incident.get('severityLevel') == 'Medium'):
                        resolution_time['medium'].append(incident.get('resolutionTimeInSec'))
                    elif(incident.get('severityLevel') == 'Low'):
                        resolution_time['low'].append(incident.get('resolutionTimeInSec'))
        resolution_time_data = {}
        for k,v in  resolution_time.items():
            if(len(v)>0):
                avg_sec = sum(v)/len(v)
                resolution_time_data[k] = self.get_time_format_from_sec(avg_sec)
            else:
                resolution_time_data[k] =""
        return resolution_time_data


    def send_email(self, to_addr, from_addr='yhemanthsai555@gmail.com', password='your_password'):
        print("in send email")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_addr, "rcxv qeec psfy sadk")
        email_message = MIMEMultipart("alternative")
        email_message['From'] = from_addr
        email_message['To'] = to_addr
        email_message['Subject'] = "Port of Alaska Alerts Service: Incident Notification"
        email_message.add_header('Reply-To', 'unsubscribe@akdot.com')    

        # HTML Message
        html_message = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #FAFAFA;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 20px auto;
                        padding: 20px;
                        background-color: #FFFFFF;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    }}
                    .header {{
                        background-color: #0056b3;
                        color: #FFFFFF;
                        padding: 10px 20px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                        border-bottom: 4px solid #004494;
                    }}
                    .header img {{
                        height: 50px;
                        /* Adjust logo height as needed */
                    }}
                    .content {{
                        padding: 20px;
                        text-align: left;
                        line-height: 1.5;
                        border-bottom: 1px solid #EEE;
                    }}
                    .signature {{
                        padding: 20px;
                        text-align: left;
                        font-size: 0.9em;
                        color: #555;
                    }}
                    .unsubscribe {{
                        font-size: 0.8em;
                        text-align: center;
                        margin-top: 10px;
                    }}
                    .unsubscribe a {{
                        color: #0056b3;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <!-- Adjust the 'src' to your logo image URL -->
                        <h2>Port of Alaska Notification Service</h2>
                    </div>
                    <div class="content">
                        <p>Dear Subscriber,</p>
                        </br>
                        <p>This is a incident notification email.</p>
                        </br>
                        <p> Thank you for subscribing and staying connected with us. Should you have any questions or concerns, please don't hesitate to contact us at <a href="mailto:portofalaska@anchorageak.gov">portofalaska@anchorageak.gov</a>.</p>
                    </div>
                    <div class="signature">
                        <p>Best Regards,</p>
                        <p>Port of Alaska Alerts Team</p>
                    </div>
                    <div class="unsubscribe">
                        <p>To unsubscribe from these notifications, please <a href="mailto:unsubscribe@anchorageak.gov?subject=Unsubscribe">click here</a>.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # The rest of your send_email function follows...

        
        # Attach the HTML message
        email_message.attach(MIMEText(html_message, 'html'))
        
        # Send the email
        server.send_message(email_message)
        server.quit()
        print("Email sent successfully!")