from argon2 import PasswordHasher
from dao.user_dao import UserDao


class UserService():
    def __init__(self):
        pass

    
    def create_user(self, user_details):
        # Create a new user
        
        try:
            if(None == user_details.get('password')):
                raise Exception()
            user_dao = UserDao()
            
            user = {}
            user['userId'] = user_details.get('username')
            user['group'] = user_details.get('group')
            user['firstname']=user_details.get('firstname')
            user['lastname']=user_details.get('lastname')
            
            ph = PasswordHasher()
            user['hashed_password'] = ph.hash(user_details.get('password'))
            if (None == user.get('userId')):
                raise Exception("No User Id")
            user_dao.create_user(user)
            return {'status':'success'}
        except Exception as e:
            return {'status':'failed', 'error':e}

    def get_user(self, user_id):
        try:
            user_dao = UserDao()
            user = user_dao.get_user(user_id)
            user_details = {}
            user_details['username'] = user.get('userId')
            user_details['group'] = user.get('group')
            return user_details
            
        except Exception as e:
            print("exception while retring the details for user - " + str(user_id))
            raise Exception("error while retriving the code ")




    
    def delete_user(self, userid):
        try:
            user_dao = UserDao()
            user_dao.delete_user(userid)
            return {'status':'success'}
        except Exception as e:
            return {'status':'failed', 'error':e}
    
    def update_user(self, user_details):
        try:

            user_dao = UserDao()
            
            user = {}
            user['userId'] = user_details.get('username')
            user['group'] = user_details.get('group')
            if(None != user_details.get('password')):
                ph = PasswordHasher()
                user['hashed_password'] = ph.hash(user_details.get('password'))
            
            user_dao.create_user(user)
            return {'status':'success'}
        except Exception as e:
            return {'status':'failed', 'error':e}

    def check_user(self, user_id):
        try:
            user_dao = UserDao()
            user = user_dao.check_user(user_id)
            if user:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def check_password(self, user_id, password):
        try:
            user_dao = UserDao()
            user = user_dao.get_all_user_details(user_id)
            if user:
                ph = PasswordHasher()
                if ph.verify(user['hashed_password'], password):
                    return True
            return False
        except Exception as e:
            return False

    


    
