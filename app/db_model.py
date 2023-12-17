from flask_login import UserMixin
from dataclasses import dataclass
from typing import List, Optional


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
    def find_all_id_name_insurance_certificate(page=False, per_page=False):
        query = "SELECT id, name, insurance_certificate FROM patients ORDER BY name"
        if page and per_page is not None:
            query += f" LIMIT {per_page} OFFSET {(page - 1) * per_page}"
        return db.execute_select(query)
    
    @staticmethod
    def get_by_id(id):
        query = "SELECT * FROM patients WHERE id = %s"
        patient_data = db.execute_select(query, id)
        if patient_data:
            return Patient(*patient_data[0])
        
    @staticmethod

    def find_all_search_lazyload(search, page, per_page):
        query = "SELECT id, name, insurance_certificate \
         FROM patients \
         WHERE MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) \
         OR MATCH(insurance_certificate) AGAINST (%s IN NATURAL LANGUAGE MODE) \
         ORDER BY (MATCH(name) AGAINST (%s IN NATURAL LANGUAGE MODE) + MATCH(insurance_certificate) AGAINST (%s IN NATURAL LANGUAGE MODE)) DESC, \
         name ASC \
         LIMIT %s OFFSET %s"
        return db.execute_select(query, search, search, search, search, per_page, (page - 1) * per_page)
    
    @staticmethod
    def insert_new_patient(name, insurance_certificate, born_date, sex):
        query = "INSERT INTO patients (name, insurance_certificate, born_date, sex) VALUES (%s, %s, %s, %s)"
        db.execute_update(query, name, insurance_certificate, born_date, sex)

    @staticmethod
    def get_id_by_insurance_certificate(insurance_certificate):
        query = "SELECT id FROM patients WHERE insurance_certificate = %s"
        result = db.execute_select(query, insurance_certificate)
        if result:
            return result[0][0]
        else:
            return None
    
    @staticmethod
    def get_name_by_request_id(request_id):
        query = "SELECT \
                     patients.name \
                 FROM patients \
                 JOIN requests ON requests.patient_id = patients.id \
                 WHERE \
                     requests.id = %s"
        result = db.execute_select(query, request_id)
        if result:
            return result[0][0]
        
        
        
class Symptom:
    def __init__(self, id, name, ru_name):
        self.id = id
        self.name = name
        self.ru_name = ru_name    
    
    @staticmethod
    def get_by_id(id):
        query = "SELECT id, name, ru_name \
                 FROM symptoms \
                 WHERE id = %s"
        values = db.execute_select(query, id)
        if values:
            return Symptom(*values[0])
        
    def find_all_symptoms():
        query = "SELECT id, ru_name FROM symptoms"
        return db.execute_select(query)
    
    @staticmethod
    def get_page_by_filter(filter, page, per_page):
        query = "SELECT id, ru_name FROM symptoms \
            WHERE MATCH (ru_name) AGAINST (%s IN NATURAL LANGUAGE MODE WITH QUERY EXPANSION) \
            LIMIT %s OFFSET %s;"  #тоже удалить можно по идее
        return db.execute_select(query, filter, per_page, (page - 1) * per_page)
    
    @staticmethod
    def get_count_by_filter(filter):
        query = "SELECT COUNT(*) FROM symptoms \
            WHERE LOWER(ru_name) LIKE %s or LOWER(name) LIKE %s"
        filter_string = f'%{filter.lower()}%'
        return db.execute_select(query, filter_string, filter_string)

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
    def add(doctor_id, patient_id, symptom_ids, ml_model_version):
        query_req = "INSERT INTO requests (doctor_id, patient_id, ml_model_id) \
                     SELECT %s, %s, ml_model.id \
                     FROM ml_model \
                     WHERE ml_model.version = %s"
        request_id = db.execute_update(query_req, doctor_id, patient_id, ml_model_version)
    
        values = ', '.join(f"({symptom_id}, {request_id})" for symptom_id in symptom_ids)
        query_req_sym = f"INSERT INTO request_symptoms (symptom_id, request_id) VALUES {values}"
        db.execute_update(query_req_sym)
        return request_id
        
    @staticmethod
    def update_status(id, status, predicted_disease_id):
        query = "UPDATE requests \
                 SET status = %s, predicted_disease_id = %s \
                 WHERE id = %s"
        db.execute_update(query, status, predicted_disease_id, id)

    @staticmethod
    def update_is_commented(id, is_commented):
        query = "UPDATE requests \
                 SET is_commented = %s \
                 WHERE id = %s" # в бд создана процедура обновления стутса комментов, статус изменяется автоматически, необходимости делать это вручную по идее нет
        db.execute_update(query, is_commented, id)

    @staticmethod
    def get_symptom_ru_names(request_id):
        query = "SELECT \
                     sym.ru_name \
                 FROM \
                     symptoms AS sym \
                 JOIN \
                     request_symptoms AS r_s ON r_s.symptom_id = sym.id \
                 WHERE \
                     r_s.request_id = %s"
        result = db.execute_select(query, request_id)
        if result:
            return [element[0] for element in result]
    
    @staticmethod
    def get_disease_ru_name(request_id):
        query = "SELECT \
                     d.ru_name \
                 FROM \
                     diseases AS d \
                 JOIN \
                     requests AS r ON r.predicted_disease_id = d.id \
                 WHERE \
                     r.id = %s"
        result = db.execute_select(query, request_id)
        if result:
            return result[0][0]
        return None
    
    @staticmethod
    def get_requests_page_by_doctor_id_contain_substr(doctor_id, page, per_page, search_text):
        query = "SELECT  \
                     requests.id, \
                     patients.name, \
                     requests.date, \
                     diseases.ru_name, \
                     requests.is_commented \
                 FROM requests \
                 JOIN doctors ON requests.doctor_id = doctors.id \
                 JOIN diseases ON requests.predicted_disease_id = diseases.id \
                 JOIN patients ON requests.patient_id = patients.id \
                 WHERE  \
                     doctors.id = %s AND \
                     (MATCH(diseases.ru_name) AGAINST (%s IN NATURAL LANGUAGE MODE) OR \
                     MATCH(patients.name) AGAINST (%s IN NATURAL LANGUAGE MODE)) \
                 ORDER BY (MATCH(diseases.ru_name) AGAINST (%s IN NATURAL LANGUAGE MODE) + MATCH(patients.name) AGAINST (%s IN NATURAL LANGUAGE MODE)) DESC, \
                 patients.name ASC, requests.date DESC \
                 LIMIT %s OFFSET %s;" 
                 
        return db.execute_select(query, doctor_id, search_text, search_text, search_text, search_text, per_page, (page - 1) * per_page)

    @staticmethod
    def get_requests_page_by_doctor_id(doctor_id, page, per_page):
        query = "SELECT  \
                     requests.id, \
                     patients.name, \
                     requests.date, \
                     diseases.ru_name, \
                     requests.is_commented \
                 FROM requests \
                 JOIN doctors ON requests.doctor_id = doctors.id \
                 JOIN diseases ON requests.predicted_disease_id = diseases.id \
                 JOIN patients ON requests.patient_id = patients.id \
                 WHERE  \
                     doctors.id = %s \
                 ORDER BY requests.date DESC, \
                 patients.name ASC \
                 LIMIT %s OFFSET %s;" 
                 
        return db.execute_select(query, doctor_id, per_page, (page - 1) * per_page)

    @staticmethod
    def get_requests_page_by_patient_id(patient_id, page, per_page):
        query = "SELECT requests.id, \
                        doctors.name, \
                        requests.date, \
                        diseases.ru_name, \
                        requests.is_commented \
                FROM requests \
                JOIN doctors ON requests.doctor_id = doctors.id \
                JOIN diseases ON requests.predicted_disease_id = diseases.id \
                WHERE requests.patient_id = %s \
                LIMIT %s OFFSET %s;"
        return db.execute_select(query, patient_id, per_page, (page - 1) * per_page)
    

class Comment:
    def __init__(self, id, doctor_id, request_id, comment, date):
        self.id = id
        self.doctor_id = doctor_id
        self.request_id = request_id
        self.comment = comment
        self.date = date

    @staticmethod
    def validate_comment_author(comment_id, user_id):
        query = "SELECT COUNT(*) FROM comments WHERE id = %s AND doctor_id = %s"
        return db.execute_select(query, comment_id, user_id)

    
    @staticmethod
    def add(doctor_id, request_id, comment):
        query = "INSERT INTO comments (doctor_id, request_id, comment, status) \
                 VALUES (%s, %s, %s, %s)"
        return db.execute_update(query, doctor_id, request_id, comment, 'NEW')
    
    @staticmethod
    def get_by_id(id):
        query = "SELECT id, doctor_id, request_id, comment, date \
                 FROM comments \
                 WHERE id = %s"
        result = db.execute_select(query, id)
        if result:
            return Comment(*result[0])
    
    @staticmethod
    def update_status_by_id(status, id):
        query = "UPDATE comments \
                 SET status = %s \
                 WHERE id = %s"
        return db.execute_update(query, status, id)

    @staticmethod
    def is_request_commented(request_id):
        query = "SELECT IF(COUNT(*) > 0, 1, 0) FROM comments \
                 WHERE request_id = %s AND status = 'NEW' LIMIT 1"
        return db.execute_select(query, request_id)[0][0]
    
    @staticmethod
    def get_comments_by_request_id(request_id, doctor_id):
        query = "SELECT \
                     comments.id AS comments_id, \
                     doctors.name, \
                     comments.date, \
                     comments.comment, \
                     CASE \
                         WHEN doctors.id = %s THEN 1 \
                         ELSE 0 \
                     END \
                 FROM \
                     comments \
                 JOIN doctors ON doctors.id = comments.doctor_id \
                 WHERE comments.request_id = %s AND \
                 comments.status = 'NEW' \
                 ORDER BY comments_id DESC"
        return db.execute_select(query, doctor_id, request_id)

        

class Disease:
    def __init__(self, id, name, ru_name):
        self.id = id
        self.name = name,
        self.ru_name = ru_name
        
    def get_by_name(name):
        query = "SELECT id, name, ru_name \
                 FROM diseases \
                 WHERE name = %s"
        values = db.execute_select(query, name)
        if values:
            return Disease(*values[0])
            

@dataclass
class DoctorComment:
    id: int
    doctor: str
    time: str
    comment: str
    editable: bool

@dataclass
class ResponseData:
    id: int
    patient_name: str
    doctor: str
    symptoms: List[str]
    diagnosis: str
    doctor_comments: List[DoctorComment]
    
@dataclass
class RequestData:
    id: int
    name: str
    date: str
    diagnosis: str
    is_commented: bool

@dataclass
class PatientData:
    id: int
    name: str
    oms: str
    birthDate: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    photo_url: Optional[str] = None
    
@dataclass
class CommentResponseData:
    id: Optional[int] = None
    old_id: Optional[int] = None
    doctor: Optional[str] = None
    time: Optional[str] = None
    comment: Optional[str] = None
    
@dataclass
class SymptomData:
    id: int
    name: str