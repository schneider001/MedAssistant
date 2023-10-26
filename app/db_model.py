from flask_login import UserMixin


from init import db

class Doctor(UserMixin):
    def __init__(self, id, username, name, password_hash, last_login):
        self.id = id
        self.username = username
        self.name = name
        self.password_hash = password_hash
        self.last_login = last_login

    @staticmethod
    def get_by_id(id):
        query = "SELECT id, username, name, password_hash, last_login \
            FROM doctors WHERE id = %s"
        user_data = db.execute_select(query, id)
        if user_data:
            return Doctor(*user_data[0])

    @staticmethod
    def get_by_username(username):
        query = "SELECT id, username, name, password_hash, last_login \
            FROM doctors WHERE username = %s"
        user_data = db.execute_select(query, username)
        if user_data:
            return Doctor(*user_data[0])



class Patient:
    def __init__(self, id, name, insurance_certificate, born_date, sex):
        self.id = id
        self.name = name
        self.insurance_certificate = insurance_certificate
        self.born_date = born_date
        self.sex = sex
        
    @staticmethod
    def find_all_id_name_insurance_certificate():
        query = "SELECT id, name, insurance_certificate FROM patients"
        return db.execute_select(query)
    
    @staticmethod
    def get_by_id(id):
        query = "SELECT * FROM patients WHERE id = %s"
        patient_data = db.execute_select(query, id)
        if patient_data:
            return Patient(*patient_data[0])
        
        
class Symptom:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    @staticmethod
    def find_all_symptoms():
        query = "SELECT id, name FROM symptoms"
        return db.execute_select(query)
        