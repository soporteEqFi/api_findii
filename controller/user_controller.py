from model.user.user_model import *

mod_user = userModel()

class userController():

    def user_create(self):
        query = mod_user.create_user()
        return query