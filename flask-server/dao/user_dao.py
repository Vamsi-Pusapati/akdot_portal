from pymongo import MongoClient
import pymongo
import os 
class UserDao():
    def __init__(self):
        self.client = MongoClient(os.environ.get("MONGO_URL"))
        self.db = self.client.akdot
        self.collection = self.db.users

    def create_user(self, user_details):
        # Create a new user
        user = self.collection.insert_one(user_details)
        return user
    

    def check_user(self, user_id):
        # Get a user by id
        user = self.collection.find_one({"userId": user_id}, projection = {"userId":1})
        return user
    

    def edit_user(self, user_details):
        # Edit a user
        user = self.collection.update_one({"userId": user_details.userId}, {"$set": user_details})
        return user
    

    def delete_user(self, userId):
        # Delete a user
        user = self.collection.delete_one({"userId": userId})
        return user
    

    def get_all_user_details(self, userId):
        # Get user details
        user = self.collection.find_one({"userId": userId}, projection = {"_id":0})
        return user
    

    def get_user(self, userId):
        # Get user details
        user = self.collection.find_one({"userId": userId}, projection = {"_id":0,"hashed_password":0})
        return user
    