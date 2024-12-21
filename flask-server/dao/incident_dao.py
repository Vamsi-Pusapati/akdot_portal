import os
from pymongo import MongoClient
import pymongo


class IncidentDao():
    def __init__(self) -> None:
        # set db connection
        self.client = MongoClient(os.environ.get("MONGO_URL"))
        self.db = self.client.akdot
        self.collection = self.db.incidents

    def create_incident(self,incident_details):
        #check if uuid already  exists in the database. If not then add it 
        #else change uuid 
        try:
            self.collection.insert_one(incident_details)
            return incident_details.get('uid')
        except Exception as e:
            print('Error creating new incident',e)
            raise e

    def update_incident(self, incident_id, incident_details):

        #update the incident
        try:
            
            update_criteria = {"uid": incident_id}
            update_operators = {"$set": {}}
            for key, value in incident_details.items():
                if key != "uid":  
                    update_operators["$set"][key] = value

            update_result = self.collection.update_one(update_criteria, update_operators)
            if update_result.matched_count == 1:
                return True
            return False
        except Exception  as e:
            print('Error updating incident',e)  
            raise e
    
    def delete_incident(self, incident_id):
        # delete the incident
        try:
            query = {'uid': incident_id}
            result = self.collection.delete_one(query)
            if result.deleted_count == 1:
                return True
            else:
                return False
        except  Exception as e:
            print('Error deleting incident',e)
            raise e        


    def get_incident(self, incident_id):
        # get the incident details and check if we need to mask any details
        try:
            projection = {"_id": 0}
            query = {'uid':incident_id}
            incident = self.collection.find_one(query,projection=projection)
            if(incident):
                return incident
            else:
                return None
        except  Exception as e:
            print('Error getting incident by id', e)
            raise e
    def get_incident_based_on_incidentType(self, incidentType):
        try:
            projection = {"_id":0}
            sort_criteria = {"dateTime": pymongo.DESCENDING}
            filter_criteria={"incidentType":incidentType}
            cursor = self.collection.find(filter_criteria, projection=projection, sort=sort_criteria)
            incidents = [doc for doc in cursor]
            self.client.close()
            return incidents
        except Exception as e:
            print('Error creating new incident',e)
            raise e

    def get_all_open_incidents(self):
        # get all the incident details and check if we need to mask any details
        try: 
            projection = {"_id": 0, "uid": 1, "incidentName": 1, "dateTime": 1}
            sort_criteria = {"dateTime": pymongo.DESCENDING}
            filter_criteria = {"status": "open"} 
            cursor = self.collection.find(filter_criteria, projection=projection, sort=sort_criteria)
            incidents = [doc for doc in cursor]
            self.client.close()
            return incidents
        except Exception as e:
            print('Error creating new incident',e)
            raise e
        
    def get_alert_incidents(self):

        try:
            projection = {"_id":0, "uid":1, "incidentName":1, "dateTime":1, "description":1, "expectedResolutionTime":1, "incidentLocation":1, "incidentType":1}
            sort_criteria = {"dataTime": pymongo.DESCENDING}
            filter_criteria = {"status": "open", "incidentType": {"$in": ["accidents_and_collisions", "maintenance"]}}
            cursor = self.collection.find(filter_criteria,projection=projection,sort = sort_criteria)
            alert_incidents = [doc for doc in cursor]
            self.client.close()
            return alert_incidents
        except Exception as e:
            print('Error while retriving alert incident',e)

    def get_subscribed_emails(self, affiliations):
        # this will return all the unique  emails that are subscribed to one of the provided affilitions
        filters = {"affiliation": {"$in": affiliations}}
        projection = {"_id": 0, "email": 1}
        try:
            # Find subscribed emails with matching affiliations
            subscribe_collection = self.db.subscribe
            cursor = subscribe_collection.find(filters, projection=projection)
            emails = list({doc.get("email") for doc in cursor})  # Extract email addresses from documents
            return emails

        except Exception as e:
            print("Error fetching subscribed emails:", e)
            raise e

        