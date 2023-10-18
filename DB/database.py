import mysql.connector
import csv
from json import loads
from hashlib import sha256
import retry

class Database:
    def __init__(self):

        with open('../configs/db_settings.json', 'r') as options_file:
        with open('../configs/db_settings.json', 'r') as options_file:
            config = loads(options_file.read())

        self.conn = mysql.connector.connect(**config)
        self.cursor = self.conn.cursor()
        self.execute_sql_script("./create_db_script.sql") #TODO добавить проверку перед выполнением, созданы ли все таблицы и связи
        self.fill_from_dataset("../datasets/Symptom-severity.csv", "symptoms")
        self.fill_from_dataset("../datasets/symptom_Description.csv", "diseases")
    
    @retry(total_tries=1)
    def safe_commit(self):
        try:
            self.conn.commit()
        except mysql.connector.Error as e:
            self.conn.rollback()
            msg = str('Function: safe_commit initiated rollback due to error during commit \n')
            logger.warning(msg) 
            raise

    # Establish MySQL database
    @retry()
    def execute_sql_script(self, script_file):
        with open(script_file, 'r') as file:
                sql_script = file.read()
                sql_commands = sql_script.split(';')
                for command in sql_commands:
                    if command.strip():
                        self.cursor.execute(command)
                self.safe_commit()
            
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

    @retry()
    def select_doctor_by_id(self, id):
        query = "SELECT id, username, name, password_hash, last_login, \
            is_blocked, image_path_location FROM doctors WHERE id = %s"
        values = (id,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone()
        
    @retry()
    def select_doctor_by_username(self, username):
        query = "SELECT id, username, name, password_hash, last_login, \
            is_blocked, image_path_location FROM doctors WHERE username = %s"
        values = (username,)
        self.cursor.execute(query, values)
        return self.cursor.fetchone() 
        
    @retry()
    def insert_doctor_credentials(self, username, password_hash): #TODO использовать хэш пароля
        query = "INSERT INTO doctors (username, password_hash) VALUES (%s, %s)"
        values = (username, password_hash)
        self.cursor.execute(query, values)
        self.safe_commit()        
            
    @retry()
    def close(self):
        self.cursor.close()
        self.conn.close()
