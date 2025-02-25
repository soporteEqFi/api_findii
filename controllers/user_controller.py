from models.user_model import *

mod_user = userModel()

class userController():

    def post_create_user(self):
        query = mod_user.create_user()
        return query
    
    def get_agent_info(self, cedula):
        query = mod_user.get_agent_info(cedula)
        return query
    
    def get_user_info(self, cedula):
        query = mod_user.get_user_info(cedula)
        return query
