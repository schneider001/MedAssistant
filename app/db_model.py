from flask_login import UserMixin, login_manager

import sys
sys.path.append("..")

from init import db, login_manager

class Doctor(UserMixin):
    def __init__(self, id, username, name, password_hash, last_login, image_path_location):
        self.id = id
        self.username = username
        self.name = name
        self.password_hash = password_hash
        self.last_login = last_login
        #self.is_blocked = is_blocked
        self.image_path_location = image_path_location

    @staticmethod
    def find_by_id(id):
        user_data = db.select_doctor_by_id(id)
        if user_data:
            return Doctor(*user_data)

    @staticmethod
    def find_by_username(username):
        user_data = db.select_doctor_by_username(username)
        if user_data:
            return Doctor(*user_data)

@login_manager.user_loader
def load_user(user_id):
    return Doctor.find_by_id(user_id)