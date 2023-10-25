import mysql.connector
import csv
from json import loads

class Database:
    def __init__(self):

        with open('../configs/db_settings.json', 'r') as options_file:
            config = loads(options_file.read())

        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor()
        self.execute_sql_script("../DB/create_db_script.sql") #TODO добавить проверку перед выполнением, созданы ли все таблицы и связи
        self.fill_from_dataset("../datasets/Symptom-severity.csv", "symptoms")#TODO correct path when model is committed
        self.fill_from_dataset("../datasets/symptom_Description.csv", "diseases")
        
    def execute_sql_script(self, script_file):
        try:
            with open(script_file, 'r') as file:
                sql_script = file.read()
                sql_commands = sql_script.split(';')
                for command in sql_commands:
                    if command.strip():
                        self.cursor.execute(command)
                self.conn.commit()
        except Exception as e:
            print(f"Error executing SQL script from file: {str(e)}") #TODO логировать ошибки, а не выводить на экран
            
    def fill_from_dataset(self, filepath, tablename):
        data_set = set()
        with open(filepath, 'r') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                data_set.add(row[0])
        for entry in data_set:
            query = f"INSERT IGNORE INTO {tablename} (name) VALUES (%s)"
            values = (entry,)
            try:
                self.cursor.execute(query, values)
            except Exception as e:
                print(f"Failed to insert values from dataset {tablename} into DB: {str(e)}")
        self.conn.commit()

    #------------------------------------------
    #Doctors's queries
    #------------------------------------------

    def select_doctor_by_id(self, id):
        query = "SELECT id, username, name, password_hash, last_login \
            FROM doctors WHERE id = %s"
        values = (id,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
        
    def select_doctor_by_username(self, username):
        query = "SELECT id, username, name, password_hash, last_login \
            FROM doctors WHERE username = %s"
        values = (username,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone() 
        
    #for testing
    def insert_doctor_credentials(self, username, password_hash): #TODO использовать хэш пароля
        try:
            query = "INSERT INTO doctors (username, password_hash) VALUES (%s, %s)"
            values = (username, password_hash)
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback() #db rolls back by itself generally
            print(f"Failed to insert doctor's credentials: {str(e)}")
            
    #------------------------------------------
    #Patient's queries
    #------------------------------------------
    
    #for testing
    def insert_patient_(self, name, insurance_certificate, born_date):
        try:
            query = "INSERT INTO patients (name, insurance_certificate, born_date) VALUES (%s, %s, %s)"
            values = (name, insurance_certificate, born_date)
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback() #db rolls back by itself generally
            print(f"Failed to insert_patient_: {str(e)}")
    
    def select_all_patients_id_name_insurance_certificate(self):
        query = "SELECT id, name, insurance_certificate FROM patients"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def select_patient_by_id(self, id):
        query = "SELECT * FROM patients WHERE id = %s"
        values = (id,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
    
    #------------------------------------------
    #Symptoms's queries
    #------------------------------------------
    
    def select_all_symptoms(self):
        query = "SELECT id, name FROM symptoms"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
