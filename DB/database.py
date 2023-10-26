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
    
    
    #example 1: execute_select("SELECT * FROM users where id = %s", id) -> [(id, name, pass)]
    #example 2: execute_select("SELECT id, name FROM users) -> [(id1, name1), (id2, name2), ...]
    #example 3: execute_select("SELECT * FROM users where id = -1") -> []
    def execute_select(self, sql_query, *values) -> list[tuple]:
        self.cursor.execute(sql_query, values)
        return self.cursor.fetchall()
    
    def execute_update(self, sql_query, *values):
        try:
            self.cursor.execute(sql_query, values)
            self.conn.commit()
        except Exception as e:
            print("Can't execute update. Traceback:\n" + str(e))
        

    #------------------------------------------
    #Doctors's queries
    #------------------------------------------
        
    #for testing
    def insert_doctor_credentials_(self, username, password_hash):
        query = "INSERT INTO doctors (username, password_hash) VALUES (%s, %s)"
        self.execute_update(query, username, password_hash)
            
    #------------------------------------------
    #Patient's queries
    #------------------------------------------
    
    #for testing
    def insert_patient_(self, name, insurance_certificate, born_date):
        query = "INSERT INTO patients (name, insurance_certificate, born_date) VALUES (%s, %s, %s)"
        self.execute_update(query, name, insurance_certificate, born_date)


    #------------------------------------------
    #Close
    #------------------------------------------

    def close(self):
        self.cursor.close()
        self.conn.close()
