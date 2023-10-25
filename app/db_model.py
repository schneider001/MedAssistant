from flask_login import UserMixin, login_manager

import sys
sys.path.append("..")

from init import db, login_manager

class Doctor(UserMixin):
    def __init__(self, id, username, name, password_hash, last_login):
        self.id = id
        self.username = username
        self.name = name
        self.password_hash = password_hash
        self.last_login = last_login

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



class Patient:
    def __init__(self, id, name, insurance_certificate, born_date, sex):
        self.id = id
        self.name = name
        self.insurance_certificate = insurance_certificate
        self.born_date = born_date
        self.sex = sex
        
    @staticmethod
    def get_all_id_name_insurance_certificate():
        patients_data = db.select_all_patients_id_name_insurance_certificate()
        return patients_data
    
    @staticmethod
    def find_by_id(id):
        patient_data = db.select_patient_by_id(id)
        if patient_data:
            return Patient(*patient_data)
        
class Symptom:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    @staticmethod
    def get_all_symptoms():
        symptoms = db.select_all_symptoms()
        return symptoms
        