import mysql.connector
from csv import reader
from json import loads
from hashlib import sha256

class Database:
    # Establish a connection to the MySQL database
    def __init__(self):

        with open('./db_settings.json', 'r') as options_file:
            config = loads(options_file.read())

        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor()
        self.execute_sql_script("./create_db_script.sql") #TODO добавить проверку перед выполнением, созданы ли все таблицы и связи
        self.fill_from_dataset("./Symptom-severity.csv", "symptoms")#TODO correct path when model is committed
        self.fill_from_dataset("./symptom_Description.csv", "diseases")
        
    # Establish MySQL database
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
            
    #Add symptoms and diseases from dataset to DB, if already exists ignore
    def fill_from_dataset (self, filepath, tablename):
        data_set = set()
        with open(filepath, 'r') as csv_file:
            reader = reader(csv_file)
            header = next(reader)
            for row in reader:
                data_set.add(row[0])
        for entry in data_set:
            query = f"INSERT IGNORE INTO {tablename} (name) VALUES (%s)"
            values = (entry,)
            self.cursor.execute(query, values)
        self.conn.commit()

    def select_doctor_by_id(self, id):
        query = "SELECT id, username, name, password_hash, last_login, is_blocked FROM doctors WHERE id = %s LIMIT 1" #why limit when it's a unique field
        values = (id,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone() #it limits to 1 here anyways
        
    def select_doctor_by_username(self, username):
        query = "SELECT id, username, name, password_hash, last_login, is_blocked FROM doctors WHERE username = %s LIMIT 1" # same abt limit
        values = (username,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone() 
        
    def insert_doctor_credentials(self, username, password_hash): #TODO использовать хэш пароля
        try:
            query = "INSERT INTO doctors (username, password_hash) VALUES (%s, %s)"
            values = (username, password_hash)
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback() #db rolls back by itself generally
            print(f"Failed to insert doctor's credentials: {str(e)}")

    def close(self):
        self.cursor.close()
        self.conn.close()
