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
        
    @staticmethod
    def find_all_search_lazyload(search, start, end):
        query = "SELECT id, name, insurance_certificate FROM patients WHERE name LIKE CONCAT('%', %s, '%') LIMIT %s, %s"
        return db.execute_select(query, search, start, end)
    
    @staticmethod
    def count_all_search(search):
        query = "SELECT COUNT(*) FROM patients WHERE name LIKE CONCAT('%', %s, '%')"
        return db.execute_select(query, search)
    
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
            WHERE LOWER(ru_name) LIKE %s or LOWER(name) LIKE %s \
            LIMIT %s OFFSET %s;"
        filter_string = f'%{filter.lower()}%'
        return db.execute_select(query, filter_string, filter_string, per_page, (page - 1) * per_page)
    
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
        query = "SELECT \
                     request_id, \
                     doctor_name, \
                     date, \
                     predicted_disease_name, \
                     comment_status \
                 FROM ( \
                     SELECT  \
                         doctors.id AS doctor_id, \
                         doctors.name AS doctor_name, \
                         requests.date AS date, \
                         diseases.ru_name AS predicted_disease_name, \
                         requests.id AS request_id, \
                     FROM  \
                         requests \
                     JOIN  \
                         doctors ON requests.doctor_id = doctors.id \
                     JOIN  \
                         diseases ON requests.predicted_disease_id = diseases.id \
                 ) AS subquery \
                 WHERE  \
                     doctor_id = %s AND ( \
                         predicted_disease_name LIKE %s OR  \
                         comment_status LIKE %s OR  \
                         date LIKE %s \
                     ) \
                 LIMIT %s OFFSET %s;"
        
        sub_str = '%' + search_text + '%'
        return db.execute_select(query, doctor_id, sub_str, sub_str, sub_str, per_page, (page - 1) * per_page)

    @staticmethod
    def get_requests_page_by_patient_id(patient_id, page, per_page):
        query = "SELECT requests.id AS request_id, \
                        doctors.name AS doctor_name, \
                        requests.date, \
                        diseases.ru_name AS predicted_disease_name, \
                        requests.is_commented AS comment_status \
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
    def add(doctor_id, request_id, comment):
        query = "INSERT INTO comments (doctor_id, request_id, comment) \
                 VALUES (%s, %s, %s)"
        return db.execute_update(query, doctor_id, request_id, comment)
    
    @staticmethod
    def get_by_id(id):
        query = "SELECT id, doctor_id, request_id, comment, date \
                 FROM comments \
                 WHERE id = %s"
        result = db.execute_select(query, id)
        if result:
            return Comment(*result[0])
    
    @staticmethod
    def delete_by_id(id):
        query = "DELETE FROM comments \
                 WHERE id = %s"
        db.execute_update(query, id)
    
    @staticmethod
    def update(id, comment_text):
        query = "UPDATE comments \
                 SET comment = %s, date = NOW() \
                 WHERE id = %s"
        db.execute_update(query, comment_text, id)
    
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
                 WHERE comments.request_id = %s \
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