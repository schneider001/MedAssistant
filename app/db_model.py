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
        query = "SELECT ru_name FROM symptoms"
        result = db.execute_select(query)
        return [item[0] for item in result]
        

class Request:
    def __init__(self, id, doctor_id, patient_id, predicted_disease_id,
                 status, date, ml_model_id):
        self.id = id
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.predicted_disease_id = predicted_disease_id
        self.status = status
        self.date = date
        self.ml_model_id = ml_model_id

    @staticmethod
    def get_requests_page_by_patient_id(patient_id, page, per_page):
        query = "SELECT requests.id AS request_id, \
                        doctors.name AS doctor_name, \
                        requests.date, \
                        diseases.ru_name AS predicted_disease_name, \
                        CASE \
                            WHEN EXISTS (SELECT 1 FROM comments WHERE comments.request_id = requests.id) THEN 'Прокомментирован' \
                            ELSE 'Без комментариев' \
                        END AS comment_status \
                FROM requests \
                JOIN doctors ON requests.doctor_id = doctors.id \
                JOIN diseases ON requests.predicted_disease_id = diseases.id \
                LEFT JOIN comments ON requests.id = comments.request_id \
                WHERE requests.patient_id = %s \
                LIMIT %s OFFSET %s;"
        return db.execute_select(query, patient_id, per_page, (page - 1) * per_page)
    

class Comment:
    def __init__(self, id, doctor_id, request_id, comment):
        self.id = id
        self.doctor_id = doctor_id
        self.request_id = request_id
        self.comment = comment